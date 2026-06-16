import os
import uuid
import numpy as np
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    VisitorLog,
    UnknownVisitor
)
from app.face_service import (
    get_embedding,
    detect_faces
)
from app.utils import save_uploaded_file
from app.faiss_service import (
    add_embedding,
    search_embedding
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
        user.id
    )

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "name": user.name
    }


@router.post("/recognize")
def recognize_user(
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
            or similarity < 0.5
        ):

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

            results.append({
                "recognized": False,
                "name": "Unknown",
                "similarity": float(similarity),
                "bbox": face["bbox"]
            })

            continue

        results.append({
            "recognized": True,
            "name": matched_user.name,
            "user_id": matched_user.id,
            "similarity": float(similarity),
            "bbox": face["bbox"]
        })

    if os.path.exists(temp_photo_path):
        os.remove(temp_photo_path)

    return {
        "faces": results
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
            or similarity < 0.5
        ):

            unknown = UnknownVisitor(
                image_path=temp_photo_path
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
        if os.path.exists(
    temp_photo_path
    ):
            os.remove(
        temp_photo_path
    )
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

    return {
        "message": (
            f"User {user.name} "
            "deleted successfully"
        )
    }