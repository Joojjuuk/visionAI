import logging
from pathlib import Path
from typing import Any

from PIL import Image

from app.config import settings
from app.services.yolo_service import yolo_service

logger = logging.getLogger(__name__)


def _get_analyzer():
    """Pick the EPI classifier backend based on settings.detection_mode."""
    if settings.detection_mode == "ollama":
        from app.services.ollama_service import analyze_worker_epi
        return analyze_worker_epi, "ollama"
    from app.services.llava_service import analyze_worker_epi
    return analyze_worker_epi, "yolo"


analyze_worker_epi, _backend_name = _get_analyzer()
logger.info("[pipeline] EPI classifier backend: %s", _backend_name)


async def run_pipeline(image_path: Path) -> dict[str, Any]:
    """
    Full EPI detection pipeline:
      1. YOLOv8  → bounding boxes for every person
      2. LLaVA   → EPI status per cropped worker (sequential to respect Ollama limits)
      3. Consolidate → structured response with stats

    Returns a dict ready to be serialised as JSON by the API router.
    """
    # ── Step 1: detect persons + helmets (open-vocabulary YOLO) ──────────────
    logger.info("[pipeline] Step 1 — YOLO-World detection (person + helmet)")
    detection = yolo_service.detect(image_path)
    persons = detection["persons"]
    helmets = detection["helmets"]

    if not persons:
        logger.info("[pipeline] No persons detected — returning empty result.")
        img = Image.open(image_path)
        return _build_response([], img.size)

    logger.info(
        "[pipeline] %d person(s) and %d helmet(s) found — classifying EPI",
        len(persons), len(helmets),
    )

    # ── Step 2: EPI analysis per person ─────────────────────────────────────
    detections: list[dict[str, Any]] = []
    for det in persons:
        logger.info("[pipeline] Step 2 — analysing worker #%02d", det["id"])
        epi = await analyze_worker_epi(image_path, det, helmets, det["id"])
        detections.append(
            {
                "id": det["id"],
                "x": det["x"],
                "y": det["y"],
                "w": det["w"],
                "h": det["h"],
                "confidence": det["confidence"],
                "helmet": epi["helmet"],
                "vest": epi["vest"],
                "role": f"Trabalhador {det['id']:02d}",
            }
        )

    # ── Step 3: consolidate stats ────────────────────────────────────────────
    logger.info("[pipeline] Step 3 — consolidating results")
    img = Image.open(image_path)
    return _build_response(detections, img.size)


def _build_response(
    detections: list[dict[str, Any]],
    image_size: tuple[int, int],
) -> dict[str, Any]:
    total = len(detections)
    ok_count = sum(1 for d in detections if d.get("helmet") and d.get("vest"))
    bad_count = total - ok_count
    pct = round(ok_count / total * 100) if total else 0
    avg_conf = (
        round(sum(d["confidence"] for d in detections) / total * 100)
        if total
        else 0
    )

    return {
        "detections": detections,
        "image_width": image_size[0],
        "image_height": image_size[1],
        "stats": {
            "total": total,
            "ok": ok_count,
            "bad": bad_count,
            "pct": pct,
            "avg_confidence": avg_conf,
        },
    }
