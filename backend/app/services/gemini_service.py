"""
PPE classification via the Google Gemini API.

Uses Gemini's multimodal capability and native structured JSON outputs
(responseSchema) — no regex parsing, typed responses guaranteed.

Key rate-limit strategy: ALL workers in an image are classified in a SINGLE
request (`analyze_workers_epi`), so an image with N people costs 1 request
instead of N. Transient 429/503 errors are retried honouring the API's
Retry-After/retryDelay hint. The pipeline falls back to local computer-vision
if Gemini is ultimately unavailable, so the analysis never hard-crashes.

Classifies per worker: helmet, vest, glasses, cap (+ a short description).
"""
import asyncio
import base64
import io
import json
import logging
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# Gemini Flash returns 429 (rate limit) / 503 (overloaded) under load. Retry
# transient errors with backoff, honouring the API's suggested delay.
_RETRYABLE_STATUS = {429, 500, 503}
_MAX_ATTEMPTS = 3
_BACKOFF_BASE = 1.5   # seconds between attempts when no hint is given
_MAX_WAIT = 8.0       # cap a single backoff so the request can't hang forever

_WORKER_PROPS = {
    "worker_index": {
        "type": "INTEGER",
        "description": "Número do trabalhador (1-based), na mesma ordem em que as imagens foram enviadas.",
    },
    "helmet": {"type": "BOOLEAN", "description": "True se houver capacete de segurança na cabeça."},
    "vest": {"type": "BOOLEAN", "description": "True se houver colete refletivo/de segurança no tronco."},
    "glasses": {"type": "BOOLEAN", "description": "True se houver óculos de proteção/segurança."},
    "cap": {"type": "BOOLEAN", "description": "True se houver boné na cabeça."},
    "description": {"type": "STRING", "description": "Frase curta resumindo cabeça e tronco do trabalhador."},
}
_REQUIRED = ["worker_index", "helmet", "vest", "glasses", "cap", "description"]

_BATCH_SCHEMA = {
    "type": "ARRAY",
    "items": {"type": "OBJECT", "properties": _WORKER_PROPS, "required": _REQUIRED},
}


def _batch_prompt(n: int) -> str:
    return (
        f"Você receberá {n} recortes de imagem, cada um mostrando UM trabalhador de "
        f"construção civil, rotulados como 'Trabalhador 1' a 'Trabalhador {n}', na ordem enviada.\n"
        "Para CADA trabalhador, verifique os Equipamentos de Proteção Individual (EPI):\n"
        "1. Capacete de proteção (helmet) na cabeça.\n"
        "2. Colete refletivo de segurança (vest) no torso.\n"
        "3. Óculos de proteção/segurança (glasses) nos olhos.\n"
        "4. Boné (cap) na cabeça (por baixo do capacete ou no lugar dele).\n\n"
        f"Retorne um ARRAY JSON com exatamente {n} objetos — um por trabalhador, na MESMA ordem — "
        "cada um com 'worker_index' (1-based) e os campos solicitados, de forma extremamente precisa."
    )


# ── Image crop (generous head/torso padding for consistent VLM context) ──────
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
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "helmet": bool(item.get("helmet", False)),
        "vest": bool(item.get("vest", False)),
        "glasses": bool(item.get("glasses", False)),
        "cap": bool(item.get("cap", False)),
        "description": item.get("description", "Não especificado"),
    }


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    """Seconds to wait before retrying — honour Retry-After / retryDelay, capped."""
    header = resp.headers.get("Retry-After")
    if header and header.strip().isdigit():
        return min(float(header.strip()), _MAX_WAIT)
    try:
        for detail in resp.json().get("error", {}).get("details", []):
            rd = detail.get("retryDelay")
            if isinstance(rd, str) and rd.endswith("s") and rd[:-1].isdigit():
                return min(float(rd[:-1]), _MAX_WAIT)
    except Exception:
        pass
    return min(_BACKOFF_BASE * attempt, _MAX_WAIT)


def _is_quota_exhausted(resp: httpx.Response) -> bool:
    """A 429 caused by hard quota/billing limits won't recover by retrying."""
    try:
        msg = resp.json().get("error", {}).get("message", "").lower()
        return "quota" in msg or "billing" in msg
    except Exception:
        return False


async def _post_with_retry(client: httpx.AsyncClient, url: str, payload: dict) -> dict:
    """POST with retry/backoff on transient 429/503/500 and network errors."""
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            resp = await client.post(url, json=payload)
            # Hard quota/billing exhaustion never recovers by retrying — fail fast
            # so the pipeline can fall back to local CV immediately.
            if resp.status_code == 429 and _is_quota_exhausted(resp):
                logger.warning("Gemini 429: cota/billing esgotada — sem retry, indo para fallback.")
                resp.raise_for_status()
            if resp.status_code in _RETRYABLE_STATUS and attempt < _MAX_ATTEMPTS:
                wait = _retry_delay(resp, attempt)
                logger.warning(
                    "Gemini %s (tentativa %d/%d) — aguardando %.1fs",
                    resp.status_code, attempt, _MAX_ATTEMPTS, wait,
                )
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except (httpx.TransportError, asyncio.TimeoutError) as exc:
            if attempt < _MAX_ATTEMPTS:
                wait = _BACKOFF_BASE * attempt
                logger.warning("Falha de rede no Gemini (tentativa %d/%d) — repetindo em %.1fs: %s",
                               attempt, _MAX_ATTEMPTS, wait, exc)
                await asyncio.sleep(wait)
                continue
            raise
    raise RuntimeError("Gemini: tentativas esgotadas")  # pragma: no cover


def _endpoint() -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )


# ── Public API ──────────────────────────────────────────────────────────────
async def analyze_workers_epi(
    image_path: Path,
    persons: list[dict[str, Any]],
    helmets: list[dict[str, Any]],  # unused; signature parity with local_cv
) -> list[dict[str, Any]]:
    """
    Classify ALL detected workers in a SINGLE Gemini request.

    Returns a list aligned 1:1 with `persons`. Raises RuntimeError on
    unrecoverable API failure so the pipeline can fall back to local CV.
    """
    del helmets
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no arquivo .env.")
    if not persons:
        return []

    parts: list[dict[str, Any]] = [{"text": _batch_prompt(len(persons))}]
    for i, person in enumerate(persons, start=1):
        parts.append({"text": f"Trabalhador {i}:"})
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": _crop_worker_b64(image_path, person)}})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _BATCH_SCHEMA,
            "temperature": 0.1,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res_json = await _post_with_retry(client, _endpoint(), payload)
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:300]
        logger.error("Erro na API do Gemini (Status %s): %s", exc.response.status_code, body)
        raise RuntimeError(f"Gemini retornou {exc.response.status_code}") from exc
    except Exception as exc:
        logger.error("Falha ao chamar o Gemini: %s", exc)
        raise RuntimeError(f"Erro de processamento no Gemini: {exc}") from exc

    candidates = res_json.get("candidates", [])
    if not candidates:
        raise RuntimeError("Nenhum resultado retornado pelo modelo Gemini.")
    content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "[]")
    arr = json.loads(content_text)
    if not isinstance(arr, list):
        raise RuntimeError("Resposta do Gemini não é um array.")

    # Map by worker_index when present, otherwise positionally.
    out: list[dict[str, Any] | None] = [None] * len(persons)
    for i, item in enumerate(arr):
        if not isinstance(item, dict):
            continue
        idx = item.get("worker_index", i + 1)
        pos = idx - 1 if isinstance(idx, int) and 1 <= idx <= len(persons) else i
        if 0 <= pos < len(persons):
            out[pos] = _normalize(item)

    result: list[dict[str, Any]] = []
    for i, item in enumerate(out, start=1):
        item = item or {"helmet": False, "vest": False, "glasses": False, "cap": False, "description": "Não detectado"}
        result.append(item)
        logger.info(
            "Worker %02d (gemini) — helmet=%-5s vest=%-5s glasses=%-5s cap=%-5s | %s",
            i, item["helmet"], item["vest"], item["glasses"], item["cap"], item["description"],
        )
    return result


async def analyze_worker_epi(
    image_path: Path,
    person: dict[str, Any],
    helmets: list[dict[str, Any]],
    worker_id: int,
) -> dict[str, Any]:
    """Single-worker convenience wrapper (kept for API parity)."""
    results = await analyze_workers_epi(image_path, [person], helmets)
    return results[0]
