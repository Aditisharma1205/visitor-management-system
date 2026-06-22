from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
import cv2
import base64
import numpy as np
from app.face_service import face_app
from app.face_service import (
    detect_faces_from_frame
)
from app.tracker import assign_track
from app.cluster_service import (
    add_to_cluster,
    get_cluster
)
from app.recognition_cache import (
    get_cached_identity,
    cache_identity
)
from app.aggregation_service import (
    aggregate_embeddings
)
from app.chroma_service import (
    search_embedding
)
from app.models import User
from app.database import SessionLocal

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

            print(
                "IMAGE SHAPE:",
                image.shape
            )
            faces = detect_faces_from_frame(
    image
)

            print(
                "FACES DETECTED:",
                len(faces)
            )
            
            for face in faces:

                embedding = face["embedding"]

                track_id = assign_track(
    embedding,
    face["bbox"]
)

                add_to_cluster(
                    track_id,
                    embedding
                )

                cluster = get_cluster(
                    track_id
                )
                print(
                    f"TRACK {track_id} "
                    f"CLUSTER SIZE: {len(cluster)}"
                )
                if len(cluster) < 5:
                    continue
                
                cached = get_cached_identity(track_id)

                if cached:

                    await websocket.send_json(
                        {
                            "recognized": True,
                            "track_id": track_id,
                            "name": cached["name"],
                            "user_id": cached["user_id"],
                            "similarity": float(similarity)
                        }
                    )

                    continue
                aggregated_embedding = (
                    aggregate_embeddings(cluster)
                )
                print(
                    f"TRACK {track_id} "
                    f"AGGREGATED"
                )
                
                user_id, similarity = (
                search_embedding(
                    aggregated_embedding
                    )
                )
                print(
                    f"USER={user_id} "
                    f"SIM={similarity}"
                )
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
        "user_id": user_id,
        "name": matched_user.name
    }
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
        db.close()
    except WebSocketDisconnect:

        print("WS DISCONNECTED")
    