"""
Offline PPE classification per person — pure local computer-vision.

This is the offline fallback backend (DETECTION_MODE=yolo / `python run.py --local`),
used when Google Gemini is not available (no internet or no API key). It runs
entirely on the machine with no external calls:
  - Helmet: YOLO-World detections from yolo_service. Hi-confidence,
    generalises across colours and image styles.
  - Vest:   HSV colour analysis on the torso region. Hi-vis safety vests
    are specifically engineered to be chromatically distinctive, so this
    is faster and more reliable than open-vocabulary detection (which we
    confirmed empirically fails on vests).

It only evaluates helmet + vest (no glasses/cap, which require the Gemini VLM).
The async function signature matches gemini_service so `pipeline.py` can swap
backends transparently.
"""
import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────────────────────────
def _crop(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    ih, iw = img.shape[:2]
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(iw, x + w)
    y2 = min(ih, y + h)
    if x2 <= x1 or y2 <= y1:
        return np.zeros((0, 0, 3), dtype=np.uint8)
    return img[y1:y2, x1:x2]


def _ratio(hsv: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> float:
    if hsv.size == 0:
        return 0.0
    mask = cv2.inRange(hsv, lo, hi)
    return float(mask.sum() / 255 / mask.size)


# ── Helmet matching ─────────────────────────────────────────────────────────
def _helmet_overlaps_person_head(
    person: dict[str, Any], helmet: dict[str, Any]
) -> bool:
    """
    A helmet detection is associated with a person when the helmet centre
    falls inside the person's upper region (head/shoulders zone — top 35%
    of the person bbox, with a small slack above the bbox top).
    """
    px, py, pw, ph = person["x_abs"], person["y_abs"], person["w_abs"], person["h_abs"]
    head_top = py - int(ph * 0.10)
    head_bot = py + int(ph * 0.35)
    head_left = px - int(pw * 0.10)
    head_right = px + pw + int(pw * 0.10)

    hx = helmet["x_abs"] + helmet["w_abs"] // 2
    hy = helmet["y_abs"] + helmet["h_abs"] // 2
    return head_left <= hx <= head_right and head_top <= hy <= head_bot


# ── Vest detection (HSV) ────────────────────────────────────────────────────
_VEST_ORANGE_LO = np.array([5, 130, 130])
_VEST_ORANGE_HI = np.array([22, 255, 255])
_VEST_YELLOW_LO = np.array([22, 100, 180])
_VEST_YELLOW_HI = np.array([45, 255, 255])
_VEST_LIME_LO   = np.array([45, 100, 180])
_VEST_LIME_HI   = np.array([75, 255, 255])


def _detect_vest(img_rgb: np.ndarray, person: dict[str, Any]) -> tuple[bool, dict[str, float]]:
    """Hi-vis torso check. Returns (is_vest, debug_ratios)."""
    x, y, w, h = person["x_abs"], person["y_abs"], person["w_abs"], person["h_abs"]
    top = y + int(h * 0.15)
    bot = y + int(h * 0.55)
    left = x + int(w * 0.10)
    right = x + w - int(w * 0.10)

    torso = _crop(img_rgb, left, top, right - left, bot - top)
    if torso.size == 0:
        return False, {}

    hsv = cv2.cvtColor(torso, cv2.COLOR_RGB2HSV)
    ratios = {
        "orange": _ratio(hsv, _VEST_ORANGE_LO, _VEST_ORANGE_HI),
        "yellow": _ratio(hsv, _VEST_YELLOW_LO, _VEST_YELLOW_HI),
        "lime":   _ratio(hsv, _VEST_LIME_LO,   _VEST_LIME_HI),
    }
    total = ratios["orange"] + ratios["yellow"] + ratios["lime"]
    return total > 0.15, ratios


# ── Public API ──────────────────────────────────────────────────────────────
async def analyze_worker_epi(
    image_path: Path,
    person: dict[str, Any],
    helmets: list[dict[str, Any]],
    worker_id: int,
) -> dict[str, bool]:
    """
    Classify a single worker's PPE status.

    Args:
        image_path:  path to the original uploaded image.
        person:      a person bbox from yolo_service.detect().
        helmets:     list of helmet bboxes from the SAME detection call.
        worker_id:   sequential worker id for logging.
    """
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        raise RuntimeError(f"Cannot read image: {image_path}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    helmet = any(_helmet_overlaps_person_head(person, hm) for hm in helmets)
    vest, vest_ratios = _detect_vest(img_rgb, person)

    logger.info(
        "Worker %02d — helmet=%-5s vest=%-5s  | vest_ratios=%s",
        worker_id, helmet, vest,
        {k: round(v, 3) for k, v in vest_ratios.items()},
    )
    return {"helmet": helmet, "vest": vest}
