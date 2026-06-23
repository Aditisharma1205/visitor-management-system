import os
import uuid
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import (
    User,
    VisitorLog,
    UnknownVisitor
)
from app.services.face_service import (
    get_embedding,
    detect_faces
)
from app.utils import save_uploaded_file

from app.services.chroma_service import (
    add_embedding,
    search_embedding,
    delete_embedding
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
from app.services.unknown_service import (
    save_unknown_face
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

    user = User(
        name=name,
        photo_path=photo_path,
        embedding_path=embedding_path
    )

    db.add(user)
    db.commit()
    db.refresh(user)

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

    for face in faces:

        embedding = face["embedding"]

        user_id, similarity = search_embedding(
            embedding
        )

        if (
            user_id is None
            or similarity < settings.threshold
        ):

            unknown_image_path = save_unknown_face(
                temp_photo_path,
                face["bbox"]
            )

            unknown = UnknownVisitor(
                image_path=unknown_image_path
            )

            db.add(unknown)
            db.commit()

            results.append({
                "recognized": False,
                "name": "Unknown",
                "similarity": float(similarity),
                "bbox": face["bbox"]
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

        active_visit.exit_time = datetime.utcnow()

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

    if (
        user.photo_path
        and os.path.exists(user.photo_path)
    ):
        os.remove(user.photo_path)

    if (
        user.embedding_path
        and os.path.exists(user.embedding_path)
    ):
        os.remove(user.embedding_path)

    db.delete(user)

    db.commit()

    delete_embedding(user_id)

    return {
        "message": (
            f"User {user.name} "
            "deleted successfully"
        )
    }
    
@router.get("/debug/chroma")
def debug_chroma():

    from backend.app.services.chroma_service import collection

    return collection.get()

@router.get("/visitor/inside")
def get_current_visitors(
    db: Session = Depends(get_db)
):

    visitors = (
        db.query(
            VisitorLog,
            User
        )
        .join(
            User,
            VisitorLog.user_id == User.id
        )
        .filter(
            VisitorLog.status == "INSIDE"
        )
        .all()
    )

    return [
        {
            "visitor_log_id": log.id,
            "user_id": user.id,
            "name": user.name,
            "entry_time": log.entry_time
        }
        for log, user in visitors
    ]

@router.get("/visitor/history")
def get_visitor_history(
    db: Session = Depends(get_db)
):

    history = (
        db.query(
            VisitorLog,
            User
        )
        .join(
            User,
            VisitorLog.user_id == User.id
        )
        .order_by(
            VisitorLog.entry_time.desc()
        )
        .all()
    )

    return [
        {
            "visitor_log_id": log.id,
            "user_id": user.id,
            "name": user.name,
            "entry_time": log.entry_time,
            "exit_time": log.exit_time,
            "status": log.status
        }
        for log, user in history
    ]
    
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

    return {
        "current_visitors":
            current_visitors,

        "total_visits":
            total_visits,

        "unknown_visitors":
            unknown_count,

        "registered_users":
            total_users
    }