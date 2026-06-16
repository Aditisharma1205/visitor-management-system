from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router
from app.database import engine
from app.models import Base
from sqlalchemy import inspect
app = FastAPI(
    title="VisionPass API",
    version="1.0.0",
    description="Face Recognition Backend using InsightFace"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "VisionPass API is running"
    }

@app.get("/tables")
def get_tables():
    inspector = inspect(engine)
    return inspector.get_table_names()