import base64
import io
import json
import logging
import re
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# NOTE: Do NOT include a JSON example with pre-filled values in the prompt.
# LLaVA will copy the example values literally, causing systematic false negatives.
_EPI_PROMPT = """You are a construction site safety inspector. Your task is PPE compliance detection.

Look at this image of a construction worker and answer TWO questions:

1. HARD HAT / HELMET: Is the person wearing a safety helmet on their head?
   - Safety helmets can be white, yellow, orange, blue, red, or any other color
   - If you see a hard hat on the head -> helmet is true
   - If the head is bare (no hat at all) -> helmet is false

2. REFLECTIVE VEST: Is the person wearing a high-visibility safety vest?
   - Safety vests are typically orange or yellow with reflective strips
   - If you see a reflective/hi-vis vest on the torso -> vest is true
   - If the person only wears a regular shirt/jacket with no vest -> vest is false

Look carefully at EACH item independently. Base your answer only on what you can see.

Your response must be ONLY a JSON object with boolean values (no text, no explanation):"""

# ─── Response parsers ─────────────────────────────────────────────────────────
_JSON_OBJ_RE  = re.compile(r'\{[^{}]*"helmet"[^{}]*\}', re.DOTALL | re.IGNORECASE)
_HELMET_RE    = re.compile(r'"helmet"\s*:\s*(true|false)', re.IGNORECASE)
_VEST_RE      = re.compile(r'"vest"\s*:\s*(true|false)',   re.IGNORECASE)


def _parse_epi_response(raw: str) -> dict[str, bool]:
    """
    Multi-strategy parser for LLaVA JSON output.
    Strategy 1: Full JSON object extraction.
    Strategy 2: Per-field regex extraction.
    Strategy 3: Keyword scan (EN + PT-BR).
    """
    logger.debug("LLaVA raw response: %r", raw)

    # Strategy 1 — full JSON object containing both keys
    m = _JSON_OBJ_RE.search(raw)
    if m:
        try:
            cleaned = m.group().replace("'", '"')
            cleaned = re.sub(r",\s*}", "}", cleaned)
            data = json.loads(cleaned)
            return {
                "helmet": bool(data.get("helmet", False)),
                "vest":   bool(data.get("vest",   False)),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 2 — extract individual key:value pairs
    hm = _HELMET_RE.search(raw)
    vm = _VEST_RE.search(raw)
    if hm or vm:
        return {
            "helmet": hm.group(1).lower() == "true" if hm else False,
            "vest":   vm.group(1).lower() == "true" if vm else False,
        }

    # Strategy 3 — keyword scan (EN + PT-BR)
    lower = raw.lower()
    helmet_pos = any(k in lower for k in [
        "wearing a helmet", "wearing a hard hat", "has a helmet", "has a hard hat",
        "helmet on", "hard hat on", "safety helmet", "helmet visible",
        "usa capacete", "com capacete", "tem capacete",
    ])
    helmet_neg = any(k in lower for k in [
        "no helmet", "no hard hat", "without helmet", "not wearing a helmet",
        "not wearing a hard hat", "sem capacete", "nao usa capacete",
    ])
    vest_pos = any(k in lower for k in [
        "wearing a vest", "safety vest", "high-visibility", "hi-vis",
        "reflective vest", "wearing a reflective",
        "usa colete", "com colete", "tem colete", "colete refletivo",
    ])
    vest_neg = any(k in lower for k in [
        "no vest", "no safety vest", "without vest", "not wearing a vest",
        "sem colete", "nao usa colete",
    ])

    result = {
        "helmet": helmet_pos and not helmet_neg,
        "vest":   vest_pos   and not vest_neg,
    }
    logger.debug("Parser strategy 3 (keywords): %s | raw: %r", result, raw[:200])
    return result


def _crop_to_base64(image_path: Path, bbox: dict[str, Any]) -> str:
    """
    Crop the worker region with generous padding:
    - 20% horizontal padding
    - 30% extra headroom above (to capture helmets)
    - 15% below
    Upscale small crops to ensure LLaVA has enough pixels to inspect details.
    """
    with Image.open(image_path) as img:
        img_w, img_h = img.size
        x, y, w, h = bbox["x_abs"], bbox["y_abs"], bbox["w_abs"], bbox["h_abs"]

        pad_x        = int(w * 0.20)
        pad_y_top    = int(h * 0.30)  # extra headroom for helmets
        pad_y_bottom = int(h * 0.15)

        left   = max(0,     x - pad_x)
        top    = max(0,     y - pad_y_top)
        right  = min(img_w, x + w + pad_x)
        bottom = min(img_h, y + h + pad_y_bottom)

        crop = img.crop((left, top, right, bottom)).convert("RGB")

        # Upscale small crops so LLaVA has enough pixels to see details
        cw, ch = crop.size
        min_side = 336  # LLaVA optimal input patch size
        if cw < min_side or ch < min_side:
            scale = max(min_side / cw, min_side / ch)
            crop = crop.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


async def analyze_worker_epi(
    image_path: Path,
    bbox: dict[str, Any],
    worker_id: int,
) -> dict[str, bool]:
    """
    Send a cropped worker image to LLaVA via Ollama and return EPI status.
    Uses /api/generate with format:json.
    """
    b64 = _crop_to_base64(image_path, bbox)

    payload = {
        "model": settings.llava_model,
        "prompt": _EPI_PROMPT,
        "images": [b64],
        "format": "json",   # Force Ollama to output valid JSON structure
        "stream": False,
        "options": {
            "temperature": 0.0,   # Deterministic — minimize hallucination
            "num_predict": 80,    # Only need {"helmet":X,"vest":X}
        },
    }

    url = f"{settings.ollama_url}/api/generate"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text: str = data.get("response", "")
    except httpx.HTTPError as exc:
        logger.error("Ollama request failed for worker %d: %s", worker_id, exc)
        return {"helmet": False, "vest": False}

    result = _parse_epi_response(raw_text)
    logger.info(
        "Worker %02d — helmet=%s  vest=%s  (raw: %r)",
        worker_id,
        result["helmet"],
        result["vest"],
        raw_text[:80],
    )
    return result
