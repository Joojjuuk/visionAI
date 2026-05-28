"""
PPE classification via an Ollama-served vision-language model.

Default model: gemma3:4b. Picked because:
  - Fits 100 % on a 6 GB VRAM GPU (loaded weights ≈ 4.3 GB), avoiding the
    CPU offload that destroys vision-encoder accuracy on bigger models.
  - Produces detailed, attribute-rich descriptions when asked to describe
    a cropped worker — which the keyword classifier then converts to
    helmet/vest booleans.

Yes/No prompts return empty or unreliable answers across most small-VL
models — descriptive prompts are the only thing that consistently works.

Used when settings.detection_mode == "ollama"; otherwise the YOLO-World
classifier in llava_service.py is used.
"""
import base64
import io
import logging
import re
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


_DESCRIBE_PROMPT = (
    "Describe this construction worker in 2-3 short sentences, focused on "
    "what they wear on their head and on their torso. Be specific about "
    "colors. If they have no hat or no vest, say so explicitly."
)


# ── Keyword classifier ──────────────────────────────────────────────────────
_HELMET_POS = [
    r"\bhard ?hat\b", r"\bhelmet\b", r"\bsafety hat\b",
    r"\bconstruction hat\b", r"\bcapacete\b",
]
_HELMET_NEG = [
    # "no [optional adjectives] hat/helmet/hardhat/headwear"
    r"\bno\s+(?:\w+\s+){0,3}(?:hat|helmet|hard ?hat|headwear|head protection)\b",
    r"\bwithout (?:a |any )?(?:hat|helmet|hard ?hat|head ?wear|head protection)\b",
    r"\bbare[- ]head(?:ed)?\b",
    r"\bnot wearing (?:a |any )?(?:hat|helmet|hard ?hat)\b",
    r"\bhead(?:wear)?\s*[:\-]?\s*(?:none|no|bare)\b",
    r"\bsem capacete\b",
]
_VEST_POS = [
    r"\bsafety vest\b", r"\breflective vest\b", r"\bhi[- ]?vis(?:ibility)? vest\b",
    r"\bhigh[- ]?visibility vest\b", r"\breflective safety vest\b",
    r"\b(?:orange|yellow|lime|neon|pink|fluorescent) vest\b",
    r"\bhi[- ]?vis(?:ibility)?\b(?=.*\bvest\b)",
    r"\bvest\b",  # bare "vest" — covered by NEG checks if absent
    r"\bcolete\b",
]
_VEST_NEG = [
    # "no [optional adjectives] vest" — covers "no vest", "no visible vest",
    # "no safety vest", "no high-visibility vest", "no visible or other vest", etc.
    r"\bno\s+(?:\w+\s+){0,4}vest\b",
    r"\bwithout (?:a |any )?vest\b",
    r"\bnot wearing (?:a |any )?vest\b",
    r"\btorso\s*[:\-]?\s*(?:none|no vest|plain)\b",
    r"\bsem colete\b",
]


def _match_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _classify(description: str) -> dict[str, bool]:
    return {
        "helmet": _match_any(_HELMET_POS, description) and not _match_any(_HELMET_NEG, description),
        "vest":   _match_any(_VEST_POS,   description) and not _match_any(_VEST_NEG,   description),
    }


# ── Image crop ──────────────────────────────────────────────────────────────
def _crop_worker_b64(image_path: Path, bbox: dict[str, Any]) -> str:
    """Crop the worker with generous head/torso padding and encode to JPEG."""
    with Image.open(image_path) as img:
        iw, ih = img.size
        x, y, w, h = bbox["x_abs"], bbox["y_abs"], bbox["w_abs"], bbox["h_abs"]
        pad_x = int(w * 0.18)
        pad_top = int(h * 0.28)
        pad_bot = int(h * 0.10)
        left = max(0, x - pad_x)
        top = max(0, y - pad_top)
        right = min(iw, x + w + pad_x)
        bottom = min(ih, y + h + pad_bot)
        crop = img.crop((left, top, right, bottom)).convert("RGB")
        cw, ch = crop.size
        target = 448
        if min(cw, ch) < target:
            scale = target / min(cw, ch)
            crop = crop.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


# ── Ollama chat call ────────────────────────────────────────────────────────
async def _describe(client: httpx.AsyncClient, image_b64: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "user", "content": _DESCRIBE_PROMPT, "images": [image_b64]}
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 220},
    }
    r = await client.post(f"{settings.ollama_url}/api/chat", json=payload)
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")


# ── Public API ──────────────────────────────────────────────────────────────
async def analyze_worker_epi(
    image_path: Path,
    person: dict[str, Any],
    helmets: list[dict[str, Any]],  # unused (YOLO mode uses it; signature compat)
    worker_id: int,
) -> dict[str, bool]:
    del helmets

    b64 = _crop_worker_b64(image_path, person)
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            description = await _describe(client, b64)
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Ollama não está rodando. Inicie 'ollama serve' ou use DETECTION_MODE=yolo."
        ) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Erro Ollama: {exc}") from exc

    result = _classify(description)
    logger.info(
        "Worker %02d (ollama) — helmet=%-5s vest=%-5s  | desc: %r",
        worker_id, result["helmet"], result["vest"],
        description.replace("\n", " ").strip()[:240],
    )
    return result
