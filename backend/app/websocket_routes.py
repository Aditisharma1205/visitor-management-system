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
from app.tracker import assign_track, tracks
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
from app.models import User, CameraSession
from app.database import SessionLocal
from starlette.websockets import WebSocketState
from app.services.zone_service import get_zone
from app.services.movement_service import detect_event
from app.services.snapshot_service import save_snapshot
from app.services.visitor_log_service import (
    create_entry,
    create_exit
)
from app.services.session_services import start_session, end_session
from app.live_state import set_live_state, clear_live_state
from app.reid_memory import (
    save_identity,
    search_memory
)

from app.services.unknown_visitor_service import create_unknown_visitor
from app.antispoof.inference import antispoof
import traceback


router = APIRouter()

# Live-ness/spoof tuning. Was hardcoded inline before; pulled to the top so
# it's easy to tune in one place.
SPOOF_SCORE_WINDOW = 10
SPOOF_MIN_SAMPLES = 5
SPOOF_LIVE_THRESHOLD = 0.7

# How much bigger than the raw face bbox to crop for the anti-spoof model.
FACE_CROP_SCALE = 2.7


def crop_face_for_antispoof(image, bbox):
    """
    Crop a padded region around a face bbox for the anti-spoof model.

    This used to be redefined as a closure inside the per-face loop of the
    websocket handler, meaning a brand new function object got allocated on
    every single face, every single frame. Hoisted out - same logic, no
    behavior change, just not re-created on every iteration.
    """

    x1, y1, x2, y2 = bbox

    w = x2 - x1
    h = y2 - y1

    cx = x1 + w / 2
    cy = y1 + h / 2

    nw = w * FACE_CROP_SCALE
    nh = h * FACE_CROP_SCALE

    x1 = int(cx - nw / 2)
    y1 = int(cy - nh / 2)
    x2 = int(cx + nw / 2)
    y2 = int(cy + nh / 2)

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.shape[1], x2)
    y2 = min(image.shape[0], y2)

    return image[y1:y2, x1:x2]


def log_visitor_event(db, track, user_id, unknown_id, event, frame, bbox, name, session_id=None):
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
            snapshot_path=snapshot_path,
            session_id=session_id
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

    # This app only ever runs one active camera feed at a time (the global
    # `tracks` dict below is shared, single-connection state), so a /ws
    # connection maps 1:1 to a CameraSession. If a session was left ACTIVE
    # from a previous connection that didn't clean up (e.g. a server
    # restart), close it out first so /session/active doesn't point at a
    # dead session forever.
    stale_session = (
        db.query(CameraSession)
        .filter(CameraSession.status == "ACTIVE")
        .first()
    )
    if stale_session:
        end_session(db, stale_session.id)
        clear_live_state(stale_session.id)

    session = start_session(db)
    session_id = session.id
    print(f"SESSION STARTED id={session_id}")

    try:

        while True:

            frame = await websocket.receive_text()
            t_start = time.time()
            print(f"Frame received: {len(frame)} bytes")

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
            frame_active_tracks = []

            for face in faces:
                bbox = face["bbox"]

                x1, y1, x2, y2 = map(int, bbox)

                height, width = image.shape[:2]

                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)

                embedding = face["embedding"]

                track_id = assign_track(
                    embedding,
                    bbox,
                    exclude_track_ids=seen_track_ids
                )
                seen_track_ids.append(track_id)
                track = tracks[track_id]

                crop = crop_face_for_antispoof(image, bbox)
                if crop is not None and crop.size > 0:
                    anti = antispoof.predict(crop)

                    if "live_scores" not in track:
                        track["live_scores"] = []
                    track["live_scores"].append(anti["live_score"])
                    if len(track["live_scores"]) > SPOOF_SCORE_WINDOW:
                        track["live_scores"].pop(0)

                    # Was sticky forever: once flagged, is_spoof could never go
                    # back to False for the life of the track, even if the
                    # rolling average recovered above the threshold on a later
                    # frame (e.g. someone briefly tilting away from camera).
                    # Now it's recomputed from the current rolling window every
                    # time we have enough samples, so it can clear again.
                    if len(track["live_scores"]) >= SPOOF_MIN_SAMPLES:
                        avg = sum(track["live_scores"]) / len(track["live_scores"])
                        is_spoof = avg < SPOOF_LIVE_THRESHOLD
                        track["is_spoof"] = is_spoof
                    else:
                        is_spoof = track.get("is_spoof", False)
                else:
                    print(f"WARNING: Empty face crop for track {track_id} at bbox {bbox}. Skipping antispoof prediction.")
                    is_spoof = track.get("is_spoof", False)
                    anti = {
                        "is_live": not is_spoof,
                        "live_score": 1.0 if not is_spoof else 0.0,
                        "spoof_score": 0.0 if not is_spoof else 1.0,
                        "print_score": 0.0,
                        "replay_score": 0.0
                    }

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
                                matched_user.name,
                                session_id
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
                            frame_active_tracks.append({
                                "track_id": track_id,
                                "name": matched_user.name,
                                "recognized": True,
                                "bbox": bbox
                            })
                            continue

                        # memory_similarity was high but no matching user
                        # row exists (stale/unknown-visitor memory entry) -
                        # previously fell through with no send_json at all,
                        # so the frontend got no bbox for this face this
                        # frame. Fall through to the provisional "unknown"
                        # send below instead of silently dropping it.

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
                    frame_active_tracks.append({
                        "track_id": track_id,
                        "name": "Unknown",
                        "recognized": False,
                        "bbox": bbox
                    })
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
                        cached["name"],
                        session_id
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
                    frame_active_tracks.append({
                        "track_id": track_id,
                        "name": cached["name"],
                        "recognized": True,
                        "bbox": bbox
                    })
                    continue

                aggregated_embedding = aggregate_embeddings(cluster)

                if aggregated_embedding is None:
                    continue

                user_id, similarity = search_embedding(
                    aggregated_embedding
                )
                memory_user, memory_similarity = search_memory(
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
                            matched_user.name,
                            session_id
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
                        frame_active_tracks.append({
                            "track_id": track_id,
                            "name": matched_user.name,
                            "recognized": True,
                            "bbox": bbox
                        })
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
                        unknown.name,
                        session_id
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
                    frame_active_tracks.append({
                        "track_id": track_id,
                        "name": unknown.name,
                        "recognized": False,
                        "bbox": bbox
                    })
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
                    matched_user.name,
                    session_id
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
                save_identity(
                    matched_user.id,
                    matched_user.name,
                    aggregated_embedding
                )
                print(
                    f"SENDING -> "
                    f"TRACK={track_id} "
                    f"NAME={matched_user.name} "
                    f"BBOX={face['bbox']}"
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
                frame_active_tracks.append({
                    "track_id": track_id,
                    "name": matched_user.name,
                    "recognized": True,
                    "bbox": bbox
                })
            # Draw recognition boxes
            for track in frame_active_tracks:

                if "bbox" not in track:
                    continue

                x1, y1, x2, y2 = map(int, track["bbox"])

                if track["recognized"]:
                    color = (0,255,0)
                else:
                    color = (0,0,255)

                cv2.rectangle(
                    image,
                    (x1,y1),
                    (x2,y2),
                    color,
                    2
                )

                label = f'{track["name"]} ({track["track_id"]})'

                cv2.putText(
                    image,
                    label,
                    (x1,max(25,y1-10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

            _, buffer = cv2.imencode(".jpg", image)

            processed_frame = base64.b64encode(buffer).decode()


            set_live_state(session_id, encoded, frame_active_tracks)

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

    except Exception as e:
        print("=" * 80)
        print("WEBSOCKET CRASH")
        traceback.print_exc()
        print("=" * 80)

    finally:

        # NOTE (unchanged behavior, flagging for visibility): tracks is a
        # single module-level dict shared by every websocket connection.
        # If more than one camera/client can connect at once, this line
        # wipes tracking state for ALL of them the moment any one client
        # disconnects, and track IDs/embeddings can cross-contaminate
        # between connections while they're both open. Left as-is since
        # this is an architecture decision (per-connection tracker state)
        # rather than a bug fix - say the word if you want that reworked.
        end_session(db, session_id)
        clear_live_state()
        tracks.clear()
        db.close()