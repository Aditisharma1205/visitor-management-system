from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
import cv2
import base64
import time
import asyncio
import numpy as np
from app.services.face_service import (
    detect_faces_from_frame
)
from app.tracker import assign_track
from app.services.cluster_service import (
    add_to_cluster,
    get_cluster
)
from app.recognition_cache import (
    get_cached_identity,
    cache_identity
)
from app.services.aggregation_service import (
    aggregate_embeddings
)
from app.services.chroma_service import (
    search_embedding
)
from app.config import settings
from app.models import User
from app.database import SessionLocal
from starlette.websockets import WebSocketState
from app.tracker import tracks
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):
    await websocket.accept()

    db = SessionLocal()
    print("WS CONNECTED")

    try:

        while True:


            frame = await websocket.receive_text()
            t_start = time.time()

            header, encoded = frame.split(
                ",",
                1
            )

            image_bytes = base64.b64decode(
                encoded
            )

            np_array = np.frombuffer(
                image_bytes,
                np.uint8
            )

            image = cv2.imdecode(
                np_array,
                cv2.IMREAD_COLOR
            )

            if image is None:
                await websocket.send_json(
                    {
                        "type": "frame_summary",
                        "active_track_ids": []
                    }
                )
                continue

            t_decoded = time.time()

            # detect_faces_from_frame is CPU-bound (InsightFace) and blocks
            # the Python interpreter. Running it directly inside this async
            # function would freeze FastAPI's entire event loop for every
            # other connection/request while it runs. Offload it to a
            # worker thread so the server stays responsive.
            faces = await asyncio.to_thread(
                detect_faces_from_frame,
                image
            )

            if websocket.client_state != WebSocketState.CONNECTED:
                print("CLIENT DISCONNECTED")
                break

            t_detected = time.time()

            seen_track_ids = []

            for face in faces:

                embedding = face["embedding"]

                track_id = assign_track(
                    embedding,
                    face["bbox"]
                )

                seen_track_ids.append(track_id)

                add_to_cluster(
                    track_id,
                    embedding
                )

                cluster = get_cluster(track_id)

                if len(cluster) < 5:
                    # Not enough samples yet to judge this face either way.
                    # Send a provisional "unknown" so the box still renders
                    # while we build confidence, instead of leaving it blank.
                    await websocket.send_json(
                        {
                            "recognized": False,
                            "track_id": track_id,
                            "name": "Unknown",
                            "similarity": 0.0,
                            "bbox": face["bbox"]
                        }
                    )
                    continue

                cached = get_cached_identity(track_id)

                if cached:

                    await websocket.send_json(
                        {
                            "type": "tracking",
                            "recognized": True,
                            "track_id": track_id,
                            "name": cached["name"],
                            "user_id": cached["user_id"],
                            "similarity": 1.0,
                            "bbox": face["bbox"]
                        }
                    )

                    continue


                aggregated_embedding = aggregate_embeddings(cluster)

                if aggregated_embedding is None:
                    continue

                user_id, similarity = search_embedding(
                    aggregated_embedding
                )

                if user_id is None or similarity < settings.threshold:

                    await websocket.send_json(
                        {
                            "recognized": False,
                            "track_id": track_id,
                            "name": "Unknown",
                            "similarity": float(similarity),
                            "bbox": face["bbox"]
                        }
                    )

                    continue

                matched_user = (
                    db.query(User)
                    .filter(User.id == user_id)
                    .first()
                )

                if matched_user is None:
                    continue

                cache_identity(
                    track_id,
                    {
                        "user_id": matched_user.id,
                        "name": matched_user.name,
                        "similarity": float(similarity)
                    }
                )
                print(
    f"SENDING -> "
    f"TRACK={track_id} "
    f"NAME={matched_user.name if 'matched_user' in locals() and matched_user else 'Unknown'} "
    f"BBOX={face['bbox']}"
)
                await websocket.send_json(
                    {
                        "recognized": True,
                        "track_id": track_id,
                        "name": matched_user.name,
                        "user_id": matched_user.id,
                        "similarity": float(similarity),
                        "bbox": face["bbox"]
                    }
                )

            t_done = time.time()

            # Tell the frontend which tracks are still actually visible in
            # this frame, so it can drop boxes for faces that left the frame
            # instead of leaving stale boxes/cards on screen.
            await websocket.send_json(
                {
                    "type": "frame_summary",
                    "active_track_ids": seen_track_ids
                }
            )

            print(
                f"decode={1000*(t_decoded - t_start):.0f}ms "
                f"detect={1000*(t_detected - t_decoded):.0f}ms "
                f"recognize={1000*(t_done - t_detected):.0f}ms "
                f"total={1000*(t_done - t_start):.0f}ms "
                f"faces={len(faces)}"
            )

    except WebSocketDisconnect:

        print("WS DISCONNECTED")

    finally:

    tracks.clear()

    db.close()