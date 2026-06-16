from pydantic import BaseModel
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    name: str
    photo_path: str
    embedding_path: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
        
        