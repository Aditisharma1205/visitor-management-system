import os
import uuid
# pyrefly: ignore [missing-import]
import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)
from sqlalchemy import func
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.utils.time_utils import now_ist
from app.models import (
    User,
    VisitorLog,
    UnknownVisitor,
    UserFaceSample,
    CameraSession
)

from app.services.face_service import (
    get_embedding,
    detect_faces
)
from app.utils.utils import save_uploaded_file

from app.services.chroma_service import (
    add_embedding,
    search_embedding,
    delete_embedding,
    collection as chroma_collection
)
from app.recognition_cache import (
    get_cached_identity,
    cache_identity
)

from app.services.cluster_service import (
    add_to_cluster,
    get_cluster,
    clear_cluster
)
from app.services.aggregation_service import (
    aggregate_embeddings
)
from app.services.snapshot_service import save_snapshot
from app.services.unknown_visitor_service import (
    create_unknown_visitor
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.post("/register")
def register_user(
    name: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    photo_path = save_uploaded_file(
        photo,
        "uploads/registered"
    )

    try:
        embedding = get_embedding(photo_path)

    except ValueError as e:

        if os.path.exists(photo_path):
            os.remove(photo_path)

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    embedding_filename = f"{uuid.uuid4()}.npy"

    embedding_path = os.path.join(
        "embeddings",
        embedding_filename
    )

    os.makedirs("embeddings", exist_ok=True)

    np.save(
        embedding_path,
        embedding
    )

    # Create the user
    user = User(
        name=name,
        photo_path=photo_path
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Save face sample
    sample = UserFaceSample(
        user_id=user.id,
        photo_path=photo_path,
        embedding_path=embedding_path
    )

    db.add(sample)
    db.commit()

    # Add embedding to ChromaDB
    add_embedding(
        embedding,
        user.id,
        user.name
    )

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "name": user.name
    }


@router.post("/visitor/check-in")
def visitor_check_in(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    temp_photo_path = save_uploaded_file(
        photo,
        "uploads/temp"
    )

    try:
        faces = detect_faces(
            temp_photo_path
        )

    except ValueError as e:

        if os.path.exists(temp_photo_path):
            os.remove(temp_photo_path)

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    results = []

    # Needed to crop+save unknown faces below. detect_faces() already reads
    # this file internally, but doesn't hand the decoded frame back to us.
    frame = cv2.imread(temp_photo_path)

    for face in faces:

        embedding = face["embedding"]

        user_id, similarity = search_embedding(
            embedding
        )

        if (
            user_id is None
            or similarity < settings.threshold
        ):

            # Previously called save_unknown_face(), which was never
            # defined/imported anywhere - this crashed with a NameError
            # on every check-in where a face wasn't recognized. Now reuses
            # the same snapshot + unknown-visitor plumbing the websocket
            # flow already relies on.
            snapshot_path = save_snapshot(
                frame,
                face["bbox"],
                "unknown",
                "checkin"
            )

            unknown = create_unknown_visitor(
                db=db,
                track_id=None,
                image_path=snapshot_path
            )

            results.append({
                "recognized": False,
                "name": "Unknown",
                "similarity": float(similarity),
                "bbox": face["bbox"],
                "unknown_id": unknown.id
            })

            continue

        matched_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if matched_user is None:
            continue

        active_visit = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.user_id == matched_user.id,
                VisitorLog.status == "INSIDE"
            )
            .first()
        )

        if active_visit:

            results.append({
                "recognized": True,
                "name": matched_user.name,
                "user_id": matched_user.id,
                "message": "Already inside"
            })

            continue

        visit = VisitorLog(
            user_id=matched_user.id
        )

        db.add(visit)
        db.commit()

        results.append({
            "recognized": True,
            "name": matched_user.name,
            "user_id": matched_user.id,
            "similarity": float(similarity),
            "status": "CHECKED_IN"
        })

    if os.path.exists(temp_photo_path):
        os.remove(temp_photo_path)

    return {
        "visitors": results
    }


@router.post("/visitor/check-out")
def visitor_check_out(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    temp_photo_path = save_uploaded_file(
        photo,
        "uploads/temp"
    )

    try:
        faces = detect_faces(
            temp_photo_path
        )

    except ValueError as e:

        if os.path.exists(temp_photo_path):
            os.remove(temp_photo_path)

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    results = []

    for face in faces:

        embedding = face["embedding"]

        user_id, similarity = search_embedding(
            embedding
        )

        if (
            user_id is None
            or similarity < settings.threshold
        ):

            results.append({
                "recognized": False,
                "name": "Unknown",
                "message": "Cannot check out unknown visitor"
            })

            continue

        matched_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if matched_user is None:

            results.append({
                "recognized": False,
                "name": "Unknown",
                "message": "User not found"
            })

            continue

        active_visit = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.user_id == matched_user.id,
                VisitorLog.status == "INSIDE"
            )
            .first()
        )

        if active_visit is None:

            results.append({
                "recognized": True,
                "name": matched_user.name,
                "message": "Visitor is not inside"
            })

            continue

        active_visit.status = "OUT"

        # Was datetime.utcnow() (naive, UTC) while every other write path
        # uses IST - see app/utils/time_utils.py for why that's a problem.
        active_visit.exit_time = now_ist()

        db.commit()

        results.append({
            "recognized": True,
            "name": matched_user.name,
            "status": "CHECKED_OUT"
        })

    if os.path.exists(temp_photo_path):

        os.remove(temp_photo_path)

    return {
        "visitors": results
    }


@router.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "photo_path": user.photo_path,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Previously this checked user.embedding_path, which doesn't exist on
    # User (it lives on UserFaceSample) - AttributeError on every call.
    # Embeddings/photos actually live in UserFaceSample rows, one per
    # registered sample.
    samples = (
        db.query(UserFaceSample)
        .filter(UserFaceSample.user_id == user_id)
        .all()
    )

    for sample in samples:
        if sample.embedding_path and os.path.exists(sample.embedding_path):
            os.remove(sample.embedding_path)
        if sample.photo_path and os.path.exists(sample.photo_path):
            os.remove(sample.photo_path)
        db.delete(sample)

    if user.photo_path and os.path.exists(user.photo_path):
        os.remove(user.photo_path)

    # VisitorLog.user_id is a FK with no ON DELETE CASCADE, so deleting a
    # user who has any visit history would previously raise an
    # IntegrityError (in addition to the embedding_path crash above).
    # Detach the history instead of deleting it, so past visits are kept.
    (
        db.query(VisitorLog)
        .filter(VisitorLog.user_id == user_id)
        .update({"user_id": None})
    )

    db.delete(user)

    db.commit()

    delete_embedding(user_id)

    return {
        "message": (
            f"User {user.name} "
            "deleted successfully"
        )
    }


def format_duration(seconds):
    if seconds < 0:
        return "0m"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes == 0:
        return "< 1m"
    return f"{minutes}m"


@router.get("/visitor/search")
def search_visitor_logs(
    name: str = None,
    start_date: str = None,
    end_date: str = None,
    user_id: int = None,
    unknown_visitor_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(VisitorLog, User, UnknownVisitor)\
        .outerjoin(User, VisitorLog.user_id == User.id)\
        .outerjoin(UnknownVisitor, VisitorLog.unknown_visitor_id == UnknownVisitor.id)

    if user_id is not None:
        query = query.filter(VisitorLog.user_id == user_id)
    elif unknown_visitor_id is not None:
        query = query.filter(VisitorLog.unknown_visitor_id == unknown_visitor_id)
    elif name:
        search_name = f"%{name}%"
        query = query.filter(
            (User.name.ilike(search_name)) |
            (VisitorLog.user_id == None) & (name.lower() == "unknown")
        )

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(VisitorLog.entry_time >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")
            query = query.filter(VisitorLog.entry_time <= end_dt)
        except ValueError:
            pass

    logs = query.order_by(VisitorLog.entry_time.desc()).all()

    results = []
    for log, user, unknown in logs:
        if user:
            visitor_name = user.name
            is_known = True
            image_path = user.photo_path
        elif unknown:
            visitor_name = f"Unknown Visitor {unknown.id}"
            is_known = False
            image_path = unknown.image_path
        else:
            visitor_name = "Unknown"
            is_known = False
            image_path = None

        # entry_time/exit_time are now consistently timezone-aware IST
        # (see models.py + time_utils.py), so this no longer needs the
        # manual tzinfo-stripping that used to paper over mixed
        # naive/aware datetimes across different write paths.
        end = log.exit_time if log.exit_time else now_ist()

        results.append({
            "visitor_log_id": log.id,
            "user_id": log.user_id,
            "unknown_visitor_id": log.unknown_visitor_id,
            "name": visitor_name,
            "is_known": is_known,
            "entry_time": log.entry_time,
            "exit_time": log.exit_time,
            "status": log.status,
            "entry_snapshot": log.entry_snapshot,
            "exit_snapshot": log.exit_snapshot,
            "image_path": image_path,
            "duration": format_duration(
                (end - log.entry_time).total_seconds()
            )
        })

    return results


@router.get("/debug/chroma")
def debug_chroma():
    # Was `from backend.app.services.chroma_service import collection`,
    # which doesn't match this project's package layout and raised
    # ModuleNotFoundError on every call. Fixed to use the already-imported
    # collection. Still no auth on this - recommend removing/gating this
    # route before any real deployment since it dumps raw embedding data.
    return chroma_collection.get()


@router.get("/visitor/inside")
def get_current_visitors(
    db: Session = Depends(get_db)
):

    # Was an INNER JOIN on User, which silently excluded every unknown
    # visitor from the "Current Visitors" table (and, after the
    # delete_user fix, would also drop any history for a since-deleted
    # user, since their logs' user_id gets nulled instead of removed).
    # CurrentVisitorsTable.jsx doesn't care whether a visitor is
    # known/unknown - it just renders name/entry_time/duration - so an
    # outer join with the same known/unknown name fallback used in
    # /visitor/search fixes this without changing the response shape the
    # frontend already expects.
    visitors = (
        db.query(VisitorLog, User, UnknownVisitor)
        .outerjoin(User, VisitorLog.user_id == User.id)
        .outerjoin(UnknownVisitor, VisitorLog.unknown_visitor_id == UnknownVisitor.id)
        .filter(VisitorLog.status == "INSIDE")
        .order_by(VisitorLog.entry_time.desc())
        .all()
    )

    results = []
    for log, user, unknown in visitors:
        if user:
            name = user.name
        elif unknown:
            name = f"Unknown Visitor {unknown.id}"
        else:
            name = "Unknown"

        results.append({
            "visitor_log_id": log.id,
            "user_id": log.user_id,
            "unknown_visitor_id": log.unknown_visitor_id,
            "name": name,
            "entry_time": log.entry_time,
            "duration": format_duration((now_ist() - log.entry_time).total_seconds())
        })

    return results


@router.get("/visitor/history")
def get_visitor_history(
    db: Session = Depends(get_db)
):

    # Same INNER JOIN issue as /visitor/inside above - fixed the same way.
    history = (
        db.query(VisitorLog, User, UnknownVisitor)
        .outerjoin(User, VisitorLog.user_id == User.id)
        .outerjoin(UnknownVisitor, VisitorLog.unknown_visitor_id == UnknownVisitor.id)
        .order_by(VisitorLog.entry_time.desc())
        .all()
    )

    results = []
    for log, user, unknown in history:
        if user:
            name = user.name
        elif unknown:
            name = f"Unknown Visitor {unknown.id}"
        else:
            name = "Unknown"

        results.append({
            "visitor_log_id": log.id,
            "user_id": log.user_id,
            "name": name,
            "entry_time": log.entry_time,
            "exit_time": log.exit_time,
            "status": log.status,
            "duration": format_duration(
                ((log.exit_time if log.exit_time else now_ist()) - log.entry_time).total_seconds()
            )
        })

    return results


@router.get("/unknown-visitors")
def get_unknown_visitors(
    db: Session = Depends(get_db)
):

    visitors = (
        db.query(UnknownVisitor)
        .order_by(
            UnknownVisitor.detected_at.desc()
        )
        .all()
    )

    return [
        {
            "id": visitor.id,
            "image_path": visitor.image_path,
            "detected_at": visitor.detected_at,
            "reviewed": visitor.reviewed
        }
        for visitor in visitors
    ]


@router.put(
    "/unknown-visitors/{visitor_id}/review"
)
def mark_unknown_visitor_reviewed(
    visitor_id: int,
    db: Session = Depends(get_db)
):

    visitor = (
        db.query(UnknownVisitor)
        .filter(
            UnknownVisitor.id == visitor_id
        )
        .first()
    )

    if visitor is None:

        raise HTTPException(
            status_code=404,
            detail="Visitor not found"
        )

    visitor.reviewed = True

    db.commit()

    return {
        "message":
            "Unknown visitor marked as reviewed"
    }


@router.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db)
):

    current_visitors = (
        db.query(VisitorLog)
        .filter(
            VisitorLog.status == "INSIDE"
        )
        .count()
    )

    total_visits = (
        db.query(VisitorLog)
        .count()
    )

    unknown_count = (
        db.query(UnknownVisitor)
        .filter(
            UnknownVisitor.reviewed == False
        )
        .count()
    )

    total_users = (
        db.query(User)
        .count()
    )

    # Today's entries & exits. Was date.today() (naive server-local date)
    # compared against IST timestamps - could be off by a day right around
    # midnight depending on server timezone. Use IST "today" consistently.
    today = now_ist().date()

    todays_entries = (
        db.query(VisitorLog)
        .filter(func.date(VisitorLog.entry_time) == today)
        .count()
    )

    todays_exits = (
        db.query(VisitorLog)
        .filter(
            VisitorLog.status == "OUT",
            func.date(VisitorLog.exit_time) == today
        )
        .count()
    )

    return {
        "current_visitors": current_visitors,
        "total_visits": total_visits,
        "unknown_visitors": unknown_count,
        "registered_users": total_users,
        "todays_entries": todays_entries,
        "todays_exits": todays_exits
    }


@router.get("/session/active")
def get_active_session(db: Session = Depends(get_db)):
    session = db.query(CameraSession)\
        .filter(CameraSession.status == "ACTIVE")\
        .first()

    if not session:
        return {"session_id": None}

    return {"session_id": session.id}


@router.get("/session/live/{session_id}")
def live_session(session_id: int):
    from app.live_state import get_live_state
    state = get_live_state()

    if state["session_id"] == session_id:
        return {
            "frame": state["frame"],
            "active_tracks": state["active_tracks"]
        }

    return {
        "frame": None,
        "active_tracks": []
    }


@router.get("/session/history")
def get_session_history(db: Session = Depends(get_db)):
    sessions = db.query(CameraSession).order_by(CameraSession.id.desc()).all()
    return [
        {
            "id": s.id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "status": s.status,
            "total_visitors": s.total_visitors,
            "known_visitors": s.known_visitors,
            "unknown_visitors": s.unknown_visitors
        }
        for s in sessions
    ]


@router.get("/session/{session_id}/visitors")
def get_session_visitors(session_id: int, db: Session = Depends(get_db)):
    session = db.query(CameraSession).filter(CameraSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    visitor_logs = []
    for log in session.logs:
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            name = user.name if user else "Unknown"
            type_visitor = "known"
        elif log.unknown_visitor_id:
            unknown = db.query(UnknownVisitor).filter(UnknownVisitor.id == log.unknown_visitor_id).first()
            name = unknown.name if unknown else f"Unknown Visitor {log.unknown_visitor_id}"
            type_visitor = "unknown"
        else:
            name = "Unknown"
            type_visitor = "unknown"

        visitor_logs.append({
            "id": log.id,
            "user_id": log.user_id,
            "unknown_visitor_id": log.unknown_visitor_id,
            "name": name,
            "type": type_visitor,
            "entry_time": log.entry_time,
            "exit_time": log.exit_time,
            "status": log.status,
            "entry_snapshot": log.entry_snapshot,
            "exit_snapshot": log.exit_snapshot
        })

    return visitor_logs
