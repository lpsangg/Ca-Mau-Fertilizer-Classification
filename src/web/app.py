"""
FastAPI Application Setup for Ca Mau Fertilizer Classification System.
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import ASSETS_DIR, BASE_DIR
from src.core.database import DatabaseManager
from src.web.api import init_api_services, router as api_router
from src.web.video_stream import VideoStreamManager

STATIC_DIR = BASE_DIR / "src" / "web" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Global instances
stream_manager: VideoStreamManager = None
db_manager: DatabaseManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global stream_manager, db_manager
    print("[SYSTEM] Starting Ca Mau Fertilizer AI Backend Services...")
    db_manager = DatabaseManager()
    stream_manager = VideoStreamManager()
    init_api_services(stream_manager, db_manager)
    yield
    print("[SYSTEM] Shutting down AI Backend Services...")
    if stream_manager:
        stream_manager.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ca Mau Fertilizer Classification & Tracking System",
        description="High-tech Industrial AI Vision System",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include REST API
    app.include_router(api_router)

    # Mount Assets
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    # Mount Web Static Files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def index():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Ca Mau Fertilizer AI Dashboard is active."}

    return app


app = create_app()
