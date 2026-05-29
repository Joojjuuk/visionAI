import logging
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
    description="Hybrid PPE detection pipeline: YOLOv8 (local) + Google Gemini 2.5 Flash (cloud).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
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


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Detection mode: %s", settings.detection_mode)
    if settings.detection_mode == "gemini":
        configured = "configured" if settings.gemini_api_key else "NOT configured"
        logger.info("Google Gemini backend — API key %s", configured)

    # Pre-load the YOLO-World model so the first request is fast.
    logger.info("Loading YOLOv8 model — %s", settings.yolo_model)
    yolo_service.load()
    logger.info("YOLOv8 ready ✓")
