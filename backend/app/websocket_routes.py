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
from app.tracker import tracks
from app.services.zone_service import get_zone
from app.services.movement_service import detect_event
from app.services.snapshot_service import save_snapshot
from app.services.visitor_log_service import (
    create_entry,
    create_exit
)
from app.reid_memory import (
    save_identity,
    search_memory
)

from app.services.unknown_visitor_service import create_unknown_visitor
from app.antispoof.inference import antispoof


router = APIRouter()
def log_visitor_event(db,track,user_id,unknown_id,event,frame,bbox,name):
    if (
        event == "ENTRY"
        and not track.get("entry_logged")
    ):

        snapshot_path = save_snapshot(
            frame,
            bbox,
            "entry",
            name
        )

        create_entry(
            db,
            user_id=user_id,
            unknown_visitor_id=unknown_id,
            snapshot_path=snapshot_path
        )

        track["entry_logged"] = True

    elif (
        event == "EXIT"
        and not track.get("exit_logged")
    ):

        snapshot_path = save_snapshot(
            frame,
            bbox,
            "exit",
            name
        )

        create_exit(
            db,
            user_id=user_id,
            unknown_visitor_id=unknown_id,
            snapshot_path=snapshot_path
        )

        track["exit_logged"] = True


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
                bbox = face["bbox"]

                x1, y1, x2, y2 = map(int, bbox)

                height, width = image.shape[:2]

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)

                def crop_face_27(image, bbox):

                    x1, y1, x2, y2 = bbox

                    w = x2 - x1
                    h = y2 - y1

                    cx = x1 + w / 2
                    cy = y1 + h / 2

                    scale = 2.7

                    nw = w * scale
                    nh = h * scale

                    x1 = int(cx - nw / 2)
                    y1 = int(cy - nh / 2)
                    x2 = int(cx + nw / 2)
                    y2 = int(cy + nh / 2)

                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(image.shape[1], x2)
                    y2 = min(image.shape[0], y2)

                    return image[y1:y2, x1:x2]
                
                embedding = face["embedding"]

                track_id = assign_track(
                    embedding,
                    bbox,
                    exclude_track_ids=seen_track_ids
                )
                seen_track_ids.append(track_id)
                track = tracks[track_id]

                crop = crop_face_27(image, bbox)
                anti = antispoof.predict(crop)

                if "live_scores" not in track:
                    track["live_scores"] = []
                track["live_scores"].append(anti["live_score"])
                if len(track["live_scores"]) > 10:
                    track["live_scores"].pop(0)

                is_spoof = False
                if len(track["live_scores"]) >= 5:
                    avg = sum(track["live_scores"]) / len(track["live_scores"])
                    if avg < 0.7:
                        track["is_spoof"] = True
                        is_spoof = True
                else:
                    is_spoof = track.get("is_spoof", False)

                if is_spoof:
                    await websocket.send_json(
                        {
                            "type": "spoof",
                            "spoof": True,
                            "message": "Spoof Attack Detected",
                            "live_score": anti["live_score"],
                            "spoof_score": anti["spoof_score"],
                            "bbox": bbox
                        }
                    )
                    continue

                zone = get_zone(bbox)

                event = detect_event(
                    track,
                    zone
                )

                print(
                    f"TRACK={track_id} "
                    f"ZONE={zone} "
                    f"EVENT={event}"
                )

                add_to_cluster(
                    track_id,
                    embedding
                )

                cluster = get_cluster(track_id)

                if len(cluster) < 5:
                    # Try to fast-match this single embedding against our active memory of recently seen users
                    memory_user, memory_similarity = search_memory(embedding)
                    if memory_similarity > 0.70:
                        matched_user = (
                            db.query(User)
                            .filter(User.id == memory_user)
                            .first()
                        )
                        if matched_user:
                            # Pre-fill the cache for this track
                            cache_identity(
                                track_id,
                                {
                                    "user_id": matched_user.id,
                                    "name": matched_user.name,
                                    "similarity": memory_similarity
                                }
                            )
                            # Refresh re-id memory with current embedding
                            save_identity(matched_user.id, matched_user.name, embedding)
                            
                            # Log visitor event if needed
                            log_visitor_event(
                            db,
                            track,
                            matched_user.id,
                            None,
                            event,
                            image,
                            bbox,
                            matched_user.name
                        )

                            await websocket.send_json(
                                {
                                    "recognized": True,
                                    "track_id": track_id,
                                    "name": matched_user.name,
                                    "user_id": matched_user.id,
                                    "similarity": memory_similarity,
                                    "bbox": bbox,
                                    "spoof": False,
                                    "live_score": anti["live_score"]
                                }
                            )
                            continue

                    # Send a provisional "unknown" so the box still renders
                    # while we build confidence, instead of leaving it blank.
                    await websocket.send_json(
                    {
                        "recognized": False,
                        "track_id": track_id,
                        "name": "Unknown",
                        "bbox": bbox,
                        "spoof": False,
                        "live_score": anti["live_score"]
                    }
                    )
                    continue

                cached = get_cached_identity(track_id)

                if cached:
                    # Refresh re-id memory with the active frame embedding
                    save_identity(cached["user_id"], cached["name"], embedding)
                    
                    log_visitor_event(
                        db,
                        track,
                        cached["user_id"],
                        None,
                        event,
                        image,
                        bbox,
                        cached["name"]
                    )
                    await websocket.send_json(
                        {
                            "type": "tracking",
                            "recognized": True,
                            "track_id": track_id,
                            "name": cached["name"],
                            "user_id": cached["user_id"],
                            "similarity": 1.0,
                            "bbox": bbox,
                            "spoof": False,
                            "live_score": anti["live_score"]
                        }
                    )

                    continue


                aggregated_embedding = aggregate_embeddings(cluster)

                if aggregated_embedding is None:
                    continue

                user_id, similarity = search_embedding(
                    aggregated_embedding
                )
                memory_user,memory_similarity = search_memory(
                    aggregated_embedding
                )

                if memory_similarity > 0.65:

                    matched_user = (
                        db.query(User)
                        .filter(
                            User.id == memory_user
                        )
                        .first()
                    )

                    if matched_user:

                        print(
                            f"RE-IDENTIFIED "
                            f"{matched_user.name}"
                        )

                        cache_identity(
                            track_id,
                            {
                                "user_id": matched_user.id,
                                "name": matched_user.name,
                                "similarity": memory_similarity
                            }
                        )

                        log_visitor_event(
                            db,
                            track,
                            matched_user.id,
                            None,
                            event,
                            image,
                            bbox,
                            matched_user.name
                        )

                    await websocket.send_json(
                        {
                            "recognized": True,
                            "track_id": track_id,
                            "name": matched_user.name,
                            "user_id": matched_user.id,
                            "similarity": memory_similarity,
                            "bbox": bbox,
                            "spoof": False,
                            "live_score": anti["live_score"]
                        }
                    )

                    continue

                if user_id is None or similarity < settings.threshold:

                    unknown = track.get("unknown_visitor")

                    if unknown is None:

                        snapshot_path = save_snapshot(
                            image,
                            bbox,
                            "unknown",
                            f"track_{track_id}"
                        )

                        unknown = create_unknown_visitor(
                            db=db,
                            track_id=track_id,
                            image_path=snapshot_path
                        )

                        track["unknown_visitor"] = unknown

                        save_identity(
                            -unknown.id,
                            "Unknown",
                            aggregated_embedding
                        )

                    log_visitor_event(
                        db,
                        track,
                        None,
                        unknown.id,
                        event,
                        image,
                        bbox,
                        unknown.name
                    )

                    await websocket.send_json(
                        {
                            "type": "unknown_alert",
                            "recognized": False,
                            "track_id": track_id,
                            "unknown_id": unknown.id,
                            "name": unknown.name,
                            "bbox": bbox,
                            "image_path": unknown.image_path,
                            "spoof": False,
                            "live_score": anti["live_score"]
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
                
                log_visitor_event(
                    db,
                    track,
                    matched_user.id,
                    None,
                    event,
                    image,
                    bbox,
                    matched_user.name
                )

                print(
                    f"TRACK={track_id} EVENT={event}"
                )
                cache_identity(
                    track_id,
                    {
                        "user_id": matched_user.id,
                        "name": matched_user.name,
                        "similarity": float(similarity)
                    }
                )
                print(
                    f"TRACK={track_id} "
                    f"EVENT={event}"
                )
                print(
                    f"SENDING -> "
                    f"TRACK={track_id} "
                    f"NAME={matched_user.name if 'matched_user' in locals() and matched_user else 'Unknown'} "
                    f"BBOX={face['bbox']}"
                )
                save_identity(
                    matched_user.id,
                    matched_user.name,
                    aggregated_embedding
                )
                await websocket.send_json(
                    {
                        "recognized": True,
                        "track_id": track_id,
                        "name": matched_user.name,
                        "user_id": matched_user.id,
                        "similarity": float(similarity),
                        "bbox": bbox,
                        "spoof": False,
                        "live_score": anti["live_score"]
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