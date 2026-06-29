from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)

from datetime import datetime
from zoneinfo import ZoneInfo
from app.database import Base
IST = ZoneInfo("Asia/Kolkata")
# existing User model remains unchanged

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    photo_path = Column(String(500), nullable=False)
    
class VisitorLog(Base):
    __tablename__ = "visitor_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    unknown_visitor_id = Column(Integer, ForeignKey("unknown_visitors.id"), nullable=True)
    entry_time = Column(
    DateTime,
    default=lambda: datetime.now(IST)
)
    exit_time = Column(DateTime, nullable=True)
    status = Column(
        String(50),
        default="INSIDE"
    )
    entry_snapshot = Column(String(500), nullable=True)
    exit_snapshot = Column(String(500), nullable=True)


class UnknownVisitor(Base):
    __tablename__ = "unknown_visitors"

    id = Column(Integer, primary_key=True, index=True)

    track_id = Column(
        Integer,
        nullable=True
    )

    image_path = Column(
        String(500),
        nullable=False
    )
    detected_at = Column(
        DateTime,
        default=lambda: datetime.now(IST)
    )
    
    last_seen = Column(
    DateTime,
    default=lambda: datetime.now(IST)
)

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
    created_at = Column(
    DateTime,
    default=lambda: datetime.now(IST)
)
    