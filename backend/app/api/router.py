import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.get("/status")
async def status() -> dict:
    """Health check endpoint — verifies YOLO loaded and Ollama reachable."""
    import httpx
    from app.services.yolo_service import yolo_service

    yolo_ok = yolo_service.is_loaded()
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{settings.ollama_url}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "yolo": "loaded" if yolo_ok else "not_loaded",
        "ollama": "connected" if ollama_ok else "unreachable",
        "model": settings.llava_model,
    }


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> JSONResponse:
    """
    Accepts an image upload, runs the full YOLOv8 → LLaVA pipeline, and
    returns structured detection data with bounding-box coordinates (% units)
    and per-worker EPI compliance status.
    """
    # ── Validation ──────────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Use JPG, PNG or WebP.",
        )

    raw = await file.read()
    if len(raw) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit.",
        )

    # ── Persist upload with a safe UUID filename ─────────────────────────────
    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    safe_name = f"{uuid4().hex}{ext}"
    upload_path = Path(settings.upload_dir) / safe_name
    upload_path.write_bytes(raw)

    logger.info("Upload saved → %s (%d bytes)", upload_path, len(raw))

    # ── Run pipeline ─────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        result = await run_pipeline(upload_path)
    except Exception as exc:
        logger.exception("Pipeline failed for %s", upload_path)
        raise HTTPException(status_code=500, detail=f"Processing error: {exc}") from exc

    duration = round(time.perf_counter() - t0, 2)
    result["duration_seconds"] = duration
    result["image_url"] = f"/uploads/{safe_name}"

    logger.info(
        "Analysis done in %.1fs — %d persons detected",
        duration,
        len(result.get("detections", [])),
    )
    return JSONResponse(content=result)
