#!/usr/bin/env python3
"""auto_change_register.py — Claude Code PostToolUse hook.

Fires after Edit/Write/MultiEdit. Appends or creates
dex-architecture/changes/CHG-YYYYMMDD-<component>.md describing the change
and flags structural changes for human/ADR review.

Reads hook JSON payload from stdin. Exits 0 always (never blocks the tool).
Logs are written to dex-architecture/changes/_hook.log on error.
"""
from __future__ import annotations

import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
DEX_ARCH = REPO_ROOT / "dex-architecture"
CHANGES_DIR = DEX_ARCH / "changes"
INDEX_FILE = DEX_ARCH / "INDEX.md"
LOG_FILE = CHANGES_DIR / "_hook.log"

# ---------------------------------------------------------------------------
# Heuristics for "structural" changes (worth flagging for ADR upgrade)
# ---------------------------------------------------------------------------

STRUCTURAL_PATTERNS: list[tuple[str, str]] = [
    (r"\.agent[\\/](agents|skills|workflows|rules)[\\/]", "agent-config"),
    (r"(^|[\\/])package\.json$", "dependencies"),
    (r"(^|[\\/])pyproject\.toml$", "dependencies"),
    (r"(^|[\\/])Cargo\.toml$", "dependencies"),
    (r"(^|[\\/])go\.mod$", "dependencies"),
    (r"[\\/]migrations[\\/]", "database"),
    (r"schema\.prisma$", "database"),
    (r"\.sql$", "database"),
    (r"[\\/](api|routes)[\\/]", "api-surface"),
    (r"[\\/]app[\\/]api[\\/]", "api-surface"),
    (r"(^|[\\/])Dockerfile$", "infrastructure"),
    (r"docker-compose.*\.ya?ml$", "infrastructure"),
    (r"\.tf$", "infrastructure"),
    (r"\.github[\\/]workflows[\\/]", "ci-cd"),
    (r"(^|[\\/])CLAUDE\.md$", "agent-rules"),
    (r"(^|[\\/])AGENT\.md$", "agent-rules"),
    (r"(^|[\\/])GEMINI\.md$", "agent-rules"),
    (r"(^|[\\/])ARCHITECTURE\.md$", "agent-rules"),
]

# Paths the hook should NEVER touch (would create infinite loops or noise).
IGNORE_PATTERNS: list[str] = [
    r"dex-architecture[\\/]",
    r"\.agent[\\/]scripts[\\/]auto_change_register\.py$",
    r"\.claude[\\/]settings\.json$",
    r"[\\/]\.git[\\/]",
    r"node_modules[\\/]",
    r"__pycache__[\\/]",
    r"\.next[\\/]",
    r"dist[\\/]",
    r"build[\\/]",
]


def classify(file_path: str) -> tuple[bool, str]:
    """Return (is_structural, component_slug)."""
    for pat, comp in STRUCTURAL_PATTERNS:
        if re.search(pat, file_path):
            return True, comp
    # Fallback component name = top-level directory under repo root
    rel = file_path.replace("\\", "/").lstrip("/")
    parts = rel.split("/")
    slug = parts[0] if parts and parts[0] else "root"
    return False, _slugify(slug)


def is_ignored(file_path: str) -> bool:
    return any(re.search(p, file_path) for p in IGNORE_PATTERNS)


def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "misc"


# ---------------------------------------------------------------------------
# CHG file management
# ---------------------------------------------------------------------------

def chg_path(component: str) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return CHANGES_DIR / f"CHG-{today}-{_slugify(component)}.md"


CHG_TEMPLATE = """# CHG-{date}-{component}

**Date:** {iso}
**Component:** `{component}`
**Status:** {status}
**needs_review:** {needs_review}

---

## Files Touched

| Tool | File |
|------|------|
{rows}

## 🧠 IA Context

_Auto-captured by `PostToolUse` hook. Last agent action wrote/edited the files above._

## 👤 Humano Context

_[Não Informado pelo Usuário — preencha ao revisar]_

## Next Action

{next_action}
"""


def append_or_create(component: str, structural: bool, tool: str, file_path: str) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    target = chg_path(component)
    row = f"| `{tool}` | `{file_path}` |"

    if target.exists():
        text = target.read_text(encoding="utf-8")
        # Append row to the Files Touched table.
        if "| Tool | File |" in text:
            text = re.sub(
                r"(\| Tool \| File \|\n\|[-| ]+\|\n)",
                lambda m: m.group(1) + row + "\n",
                text,
                count=1,
            )
            # Upgrade needs_review if this edit is structural.
            if structural and "**needs_review:** false" in text:
                text = text.replace(
                    "**needs_review:** false", "**needs_review:** true", 1
                )
            target.write_text(text, encoding="utf-8")
        else:
            target.write_text(text + "\n" + row + "\n", encoding="utf-8")
        return target

    content = CHG_TEMPLATE.format(
        date=today,
        component=component,
        iso=iso,
        status="open",
        needs_review="true" if structural else "false",
        rows=row,
        next_action=(
            "**Structural change detected.** Review on next turn and offer to "
            "upgrade to an ADR via `dex-doc-register`."
            if structural
            else "Routine change. Will be summarized on `dex-doc-register` sweep."
        ),
    )
    target.write_text(content, encoding="utf-8")
    _index_append(target.name, component, today)
    return target


# ---------------------------------------------------------------------------
# INDEX.md maintenance (idempotent row insert)
# ---------------------------------------------------------------------------

def _index_append(filename: str, component: str, date: str) -> None:
    if not INDEX_FILE.exists():
        return
    text = INDEX_FILE.read_text(encoding="utf-8")
    placeholder = "| _(none yet — first Edit/Write will create one)_ | — | — |"
    new_row = f"| [{filename}](changes/{filename}) | `{component}` | {date} |"
    if placeholder in text:
        text = text.replace(placeholder, new_row)
    elif new_row in text:
        return  # idempotent
    else:
        # Insert above the standards section.
        text = re.sub(
            r"(## changes/[^\n]*\n(?:[^\n]*\n)+?\| CHG \| Component \| Date \|\n\|[-| ]+\|\n)",
            lambda m: m.group(1) + new_row + "\n",
            text,
            count=1,
        )
    INDEX_FILE.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Hook entry point
# ---------------------------------------------------------------------------

def extract_file_paths(payload: dict) -> Iterable[str]:
    """Pull file_path(s) from Edit/Write/MultiEdit tool input shapes."""
    tool_input = payload.get("tool_input", {}) or {}
    if "file_path" in tool_input:
        yield tool_input["file_path"]
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        # MultiEdit shares one file_path in tool_input itself, but defensive:
        for _ in edits:
            yield tool_input.get("file_path", "")


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except Exception:
        return 0  # never block the tool call

    tool = payload.get("tool_name", "unknown")
    if tool not in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return 0

    try:
        CHANGES_DIR.mkdir(parents=True, exist_ok=True)
        seen: set[str] = set()
        for fp in extract_file_paths(payload):
            if not fp or fp in seen:
                continue
            seen.add(fp)
            if is_ignored(fp):
                continue
            structural, component = classify(fp)
            append_or_create(component, structural, tool, fp)
    except Exception:
        try:
            CHANGES_DIR.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("a", encoding="utf-8") as fh:
                fh.write(
                    f"[{datetime.now(timezone.utc).isoformat()}] hook error:\n"
                )
                fh.write(traceback.format_exc())
                fh.write("\n")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
