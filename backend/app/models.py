from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.time_utils import now_ist

# existing User model remains unchanged in shape/columns


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    photo_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_ist)


class CameraSession(Base):
    __tablename__ = "camera_sessions"

    id = Column(Integer, primary_key=True, index=True)

    start_time = Column(DateTime(timezone=True), default=now_ist)
    end_time = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(20), default="ACTIVE")  # ACTIVE / ENDED

    total_visitors = Column(Integer, default=0)
    known_visitors = Column(Integer, default=0)
    unknown_visitors = Column(Integer, default=0)

    logs = relationship("VisitorLog", back_populates="session")


class VisitorLog(Base):
    __tablename__ = "visitor_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("camera_sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    unknown_visitor_id = Column(Integer, ForeignKey("unknown_visitors.id"), nullable=True)
    entry_time = Column(DateTime(timezone=True), default=now_ist)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        String(50),
        default="INSIDE"
    )
    entry_snapshot = Column(String(500), nullable=True)
    exit_snapshot = Column(String(500), nullable=True)

    session = relationship("CameraSession", back_populates="logs")


class UnknownVisitor(Base):
    __tablename__ = "unknown_visitors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=True)

    track_id = Column(
        Integer,
        nullable=True
    )

    image_path = Column(
        String(500),
        nullable=False
    )
    detected_at = Column(DateTime(timezone=True), default=now_ist)

    last_seen = Column(DateTime(timezone=True), default=now_ist)

    reviewed = Column(
        Boolean,
        default=False
    )


class UserFaceSample(Base):
    __tablename__ = "user_face_samples"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    photo_path = Column(String(500), nullable=False)
    embedding_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_ist)
