from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)

from datetime import datetime
from app.database import Base

# existing User model remains unchanged

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    photo_path = Column(String, nullable=False)

    embedding_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    entry_time = Column(DateTime, default=datetime.utcnow)

    exit_time = Column(DateTime, nullable=True)

    status = Column(String, default="INSIDE")


class UnknownVisitor(Base):
    __tablename__ = "unknown_visitors"

    id = Column(Integer, primary_key=True, index=True)

    image_path = Column(String, nullable=False)

    detected_at = Column(DateTime, default=datetime.utcnow)

    reviewed = Column(Boolean, default=False)
