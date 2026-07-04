import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.database import engine
from app.models import Base
from app.websocket_routes import router as ws_router

app = FastAPI(
    title="VisionPass API",
    version="1.0.0",
    description="Face Recognition Backend using InsightFace"
)

app.include_router(ws_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# StaticFiles() raises FileNotFoundError at import time if the directory
# doesn't exist yet (e.g. a fresh checkout before the first upload/snapshot
# has been written) - make sure it's there first.
os.makedirs("uploads", exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "VisionPass API is running"
    }

