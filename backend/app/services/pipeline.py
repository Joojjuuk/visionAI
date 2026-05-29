import logging
from pathlib import Path
from typing import Any

from PIL import Image

from app.config import settings
from app.services.yolo_service import yolo_service

logger = logging.getLogger(__name__)


async def _local_cv(image_path: Path, persons: list[dict], helmets: list[dict]) -> list[dict[str, Any]]:
    """Offline fallback: helmet (YOLO) + vest (HSV), per worker."""
    from app.services.local_cv_service import analyze_worker_epi as cv_analyze
    return [await cv_analyze(image_path, p, helmets, p["id"]) for p in persons]


async def _classify(image_path: Path, persons: list[dict], helmets: list[dict]) -> list[dict[str, Any]]:
    """
    Classify every detected worker's EPI, returning a list aligned with `persons`.

    Gemini mode classifies all workers in ONE request (rate-limit friendly) and
    transparently falls back to local computer-vision if the API is unavailable
    (e.g. 429/503 after retries) so the analysis never hard-fails.
    """
    if settings.detection_mode == "gemini":
        from app.services.gemini_service import analyze_workers_epi
        try:
            return await analyze_workers_epi(image_path, persons, helmets)
        except Exception as exc:
            logger.warning(
                "[pipeline] Gemini indisponível (%s) — usando fallback de visão computacional local.",
                exc,
            )
            return await _local_cv(image_path, persons, helmets)
    return await _local_cv(image_path, persons, helmets)


logger.info("[pipeline] EPI classifier backend: %s", settings.detection_mode)


async def run_pipeline(image_path: Path) -> dict[str, Any]:
    """
    Full EPI detection pipeline:
      1. YOLOv8  → bounding boxes for every person
      2. Gemini  → EPI status for all cropped workers (single multimodal request)
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

    # ── Step 2: EPI analysis (one batched call in Gemini mode) ───────────────
    epi_results = await _classify(image_path, persons, helmets)

    detections: list[dict[str, Any]] = []
    for det, epi in zip(persons, epi_results):
        entry = {
            "id": det["id"],
            "x": det["x"],
            "y": det["y"],
            "w": det["w"],
            "h": det["h"],
            "confidence": det["confidence"],
            "helmet": epi.get("helmet", False),
            "vest": epi.get("vest", False),
            "role": f"Trabalhador {det['id']:02d}",
        }
        # glasses/cap only exist in the Gemini backend; omit them in local-CV
        # mode so the frontend treats them as "not evaluated" (compliant).
        if "glasses" in epi:
            entry["glasses"] = epi["glasses"]
        if "cap" in epi:
            entry["cap"] = epi["cap"]
        detections.append(entry)

    # ── Step 3: consolidate stats ────────────────────────────────────────────
    logger.info("[pipeline] Step 3 — consolidating results")
    img = Image.open(image_path)
    return _build_response(detections, img.size)


def _build_response(
    detections: list[dict[str, Any]],
    image_size: tuple[int, int],
) -> dict[str, Any]:
    total = len(detections)
    # Compliance = helmet + vest + glasses + NO cap. glasses/cap default to
    # "compliant" when the backend didn't evaluate them (local-CV mode), so
    # this rule matches the frontend's computeStatus exactly.
    ok_count = sum(
        1
        for d in detections
        if d.get("helmet")
        and d.get("vest")
        and d.get("glasses", True)
        and not d.get("cap", False)
    )
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
