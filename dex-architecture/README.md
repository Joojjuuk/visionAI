# dex-architecture/

Source-of-truth for system specs. Auto-maintained by any agent that touches code.

## Layout

| Folder | What | Format | Owner |
|--------|------|--------|-------|
| `decisions/` | Architecture Decision Records | `ADR-NNN-titulo.md` | Humano + IA (via `dex-doc-register`) |
| `solutions/` | Postmortems / problem solutions | `SOL-YYYYMMDD-titulo.md` | IA on bug fix; humano on RCA |
| `changes/` | Day-to-day system changes | `CHG-YYYYMMDD-componente.md` | **Auto (hook)** + IA enrichment |
| `standards/` | Conventions, lint rules, patterns | `STD-titulo.md` | Humano (rare) |
| `architecture.md` | Master C4 doc | Single file | `dex-create-architecture` |
| `INDEX.md` | Navigation index | Tables | Hook + `dex-doc-register` |

## Auto-trigger flow

```
User asks for code change
   ↓
Agent does Edit/Write on src/ (etc.)
   ↓
PostToolUse hook fires → .agent/scripts/auto_change_register.py
   ↓
Script appends/updates dex-architecture/changes/CHG-YYYYMMDD-<component>.md
   ↓
On structural change (new route, schema diff, new dep, new agent/skill):
   → marks file with `needs_review: true`
   → agent reads it on next turn and offers to upgrade to ADR/SOL
```

## What counts as a structural change?

The hook script considers a write structural when path matches:

- `*/agents/*.md`, `*/skills/*.md`, `*/workflows/*.md` — agent/skill/workflow changes
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` — dependency changes
- `*/migrations/*`, `schema.prisma`, `*.sql` — DB changes
- `*/api/*`, `*/routes/*`, `*/app/api/*` — API surface changes
- `Dockerfile`, `docker-compose*.yml`, `*.tf`, `.github/workflows/*` — infra/CI
- `CLAUDE.md`, `AGENT.md`, `GEMINI.md`, `ARCHITECTURE.md` — agent rules

Other writes get logged as plain CHG but flagged `routine: true`.
