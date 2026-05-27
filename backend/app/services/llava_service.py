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

# Strict prompt — asks for JSON only so parsing is deterministic
_EPI_PROMPT = (
    "You are a workplace safety inspector. "
    "Look carefully at this cropped image of a single construction worker. "
    "Determine with high confidence:\n"
    "1. Is the person wearing a safety helmet / hard hat?\n"
    "2. Is the person wearing a reflective safety vest?\n\n"
    "Respond ONLY with a valid JSON object — no explanation, no markdown:\n"
    '{"helmet": true, "vest": false}'
)

# Matches the first {...} block the model emits
_JSON_RE = re.compile(r"\{[^}]+\}", re.DOTALL)


def _parse_epi_response(raw: str) -> dict[str, bool]:
    """
    Robustly extract {helmet, vest} from the LLaVA text response.
    Falls back to False for each key if parsing fails.
    """
    match = _JSON_RE.search(raw)
    if match:
        try:
            data = json.loads(match.group())
            return {
                "helmet": bool(data.get("helmet", False)),
                "vest": bool(data.get("vest", False)),
            }
        except json.JSONDecodeError:
            pass

    # Last-resort keyword scan
    lower = raw.lower()
    return {
        "helmet": "helmet" in lower and "no helmet" not in lower and "without helmet" not in lower,
        "vest": "vest" in lower and "no vest" not in lower and "without vest" not in lower,
    }


def _crop_to_base64(image_path: Path, bbox: dict[str, int]) -> str:
    """Crop the worker region from the full image and encode as base64 JPEG."""
    with Image.open(image_path) as img:
        x, y, w, h = bbox["x_abs"], bbox["y_abs"], bbox["w_abs"], bbox["h_abs"]
        # Add slight padding so the model sees the full figure
        pad_x = int(w * 0.05)
        pad_y = int(h * 0.05)
        left = max(0, x - pad_x)
        top = max(0, y - pad_y)
        right = min(img.width, x + w + pad_x)
        bottom = min(img.height, y + h + pad_y)

        crop = img.crop((left, top, right, bottom)).convert("RGB")

    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


async def analyze_worker_epi(
    image_path: Path,
    bbox: dict[str, Any],
    worker_id: int,
) -> dict[str, bool]:
    """
    Send a cropped worker image to LLaVA via Ollama and return EPI status.

    Returns:
        {"helmet": bool, "vest": bool}
    """
    b64 = _crop_to_base64(image_path, bbox)

    payload = {
        "model": settings.llava_model,
        "messages": [
            {
                "role": "user",
                "content": _EPI_PROMPT,
                "images": [b64],
            }
        ],
        "stream": False,
    }

    url = f"{settings.ollama_url}/api/chat"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text: str = data.get("message", {}).get("content", "")
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
