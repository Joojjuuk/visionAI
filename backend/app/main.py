import logging
import os
import socket
import subprocess
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.config import settings
from app.services.yolo_service import yolo_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Ensure upload and static dirs exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.static_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="VisionAI — EPI Detection API",
    description="Local PPE detection pipeline using YOLOv8 + LLaVA via Ollama.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Serve uploaded images so the browser can reference them
app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_dir),
    name="uploads",
)

# Serve compiled frontend (production mode)
static_path = Path(settings.static_dir)
if static_path.exists() and any(static_path.iterdir()):
    app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="static")
    logger.info("Frontend static build is being served at /")


def _is_ollama_running() -> bool:
    """Check if port 11434 is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", 11434)) == 0


def _ensure_ollama_running() -> None:
    """Check if Ollama is running and start it in background if off."""
    if _is_ollama_running():
        logger.info("Ollama service is already active ✓")
        return

    logger.warning("Ollama is offline. Starting 'ollama serve' in background...")
    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = 0x08000000  # CREATE_NO_WINDOW

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )

        for _ in range(20):
            time.sleep(0.5)
            if _is_ollama_running():
                logger.info("Ollama service started automatically ✓")
                return
        logger.error("Ollama took too long to start. Please run it manually.")
    except Exception as e:
        logger.error("Could not auto-start Ollama: %s", e)


@app.on_event("startup")
async def startup_event() -> None:
    # 1. Start Ollama in background if not active
    _ensure_ollama_running()

    # 2. Pre-load YOLO model
    logger.info("Loading YOLOv8 model — %s", settings.yolo_model)
    yolo_service.load()
    logger.info("YOLOv8 ready ✓")
