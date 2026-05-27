# DEX Flow Kit — Unified Agent Squad

Complete AI agent squad for corporate projects. Consolidated namespace under **`dex-*`** since 2026-05-24 (Antigravity + DEX BMAD personas merged).

> Full system map: [ARCHITECTURE.md](ARCHITECTURE.md)
> Rules: [rules/AGENT.md](rules/AGENT.md) (mirror of root `CLAUDE.md`) · [rules/GEMINI.md](rules/GEMINI.md)
> Spec output: [`/dex-architecture/`](../dex-architecture/) (auto-maintained)

---

## 🤖 The Squad (20 agents)

All under [agents/](agents/), named `dex-<role>.md`.

| Tier | Agent | Role | Persona (if any) |
|------|-------|------|------------------|
| **Coordination** | `dex-orchestrator` | Multi-agent dispatch | — |
| | `dex-planner` | Discovery + task planning | — |
| **Product** | `dex-product` | Strategy + PM + PO | 📊 Ana |
| | `dex-ux` | UX design | 🎨 Maya |
| | `dex-data` | Data analysis | 📈 Iris |
| **Engineering** | `dex-frontend` | Web UI implementation | — |
| | `dex-backend` | API + server systems | ⚙️ Kai |
| | `dex-database` | Schema, RLS, Postgres/Supabase | 🗄️ Viktor |
| | `dex-mobile` | iOS/Android/RN | — |
| | `dex-game` | Game development | — |
| **Quality** | `dex-qa` | Tests + automation + release | 🔍 Luna |
| | `dex-debugger` | Root cause analysis | — |
| | `dex-performance` | Web Vitals, profiling | — |
| **Operations** | `dex-devops` | CI/CD, Docker | — |
| | `dex-security` | Defensive + offensive | 🔐 Rex |
| | `dex-compliance` | Regulatory / privacy | — |
| **Growth** | `dex-seo` | SEO + GEO | — |
| **Support** | `dex-documentation` | Manuals, docs | — |
| | `dex-archaeologist` | Legacy refactor | — |
| | `dex-explorer` | Codebase analysis | — |

---

## ⚡ Standalone Skills (selected)

Under [skills/](skills/). Always prefix `dex-`. Full list: [ARCHITECTURE.md](ARCHITECTURE.md).

| Skill | What |
|-------|------|
| `dex-help` | Smart guide — "what should I do next?" |
| `dex-quick-dev` | Clarify → Plan → Build → Review fast loop |
| `dex-code-review` | 6-dimension review + Antigravity checklist |
| `dex-create-prd` | Step-by-step PRD generation |
| `dex-create-architecture` | C4 model system design |
| `dex-dev-story` | Rigorous story implementation |
| `dex-doc-register` | ADR/SOL/CHG/STD registry (auto-trigger aware) |
| `dex-skills-guide` | How to build new skills |

---

## 📂 File Layout

```
.agent/
├── agents/           # 20 dex-* persona files
├── skills/           # 37 dex-* skill modules
├── workflows/        # 11 /dex-* slash commands
├── rules/            # AGENT.md (clone of /CLAUDE.md) + GEMINI.md
├── scripts/          # auto_change_register.py + master validators
└── ARCHITECTURE.md   # System map
└── README.md         # This file

dex-architecture/     # ⭐ Auto-spec output
├── INDEX.md
├── decisions/        # ADR-NNN-*.md
├── solutions/        # SOL-YYYYMMDD-*.md
├── changes/          # CHG-YYYYMMDD-*.md (auto-created on Edit/Write)
└── standards/        # STD-*.md

.claude/
└── settings.json     # PostToolUse hook → auto_change_register.py
```

---

## 🗺️ Recommended Flow

```
1. DISCOVERY
   dex-product → PRD / OKRs / PRFAQ
   dex-planner → Task breakdown
        ↓
2. DESIGN
   dex-ux → User flow, wireframe
   dex-frontend → Implementation prep
   dex-system-design (skill) → Architecture
        ↓
3. PLANNING
   dex-planner → Sprint plan
   dex-qa → Test strategy
        ↓
4. IMPLEMENTATION
   dex-backend / dex-frontend / dex-mobile / dex-database
   dex-dev-story (skill) — for rigorous story-driven dev
   dex-quick-dev (skill) — for small tasks
        ↓
5. QUALITY & RELEASE
   dex-qa → Edge cases, release gate
   dex-code-review (skill)
   dex-security → Pre-deploy audit
        ↓
6. POST-LAUNCH
   dex-data → KPIs, insights
   dex-product → Roadmap update
```

Every step's Edit/Write is logged automatically in `dex-architecture/changes/`.

---

## 🚀 How to invoke

### An agent
Type the agent name. The agent reads its own `.md`, applies skills declared in frontmatter, and announces `🤖 Applying knowledge of @dex-<agent>...` before any code/design output.

```
dex-product
dex-backend
dex-qa
```

### A skill (standalone)
```
dex-quick-dev
dex-code-review
dex-create-prd
```

### A workflow (slash command)
```
/dex-create
/dex-orchestrate
/dex-debug
```

### Navigation
```
dex-help
dex-help Terminei o PRD, e agora?
```

---

## 🤖 Auto-Spec Trigger (NEW)

**Every code edit creates/updates a spec.** No more silent changes.

- `Edit`/`Write`/`MultiEdit` → [.agent/scripts/auto_change_register.py](scripts/auto_change_register.py) fires via `PostToolUse` hook
- Writes `dex-architecture/changes/CHG-YYYYMMDD-<component>.md`
- Flags structural changes (`needs_review: true`) for human/ADR review
- Active agent reads open CHGs before finishing the turn and offers ADR promotion

Bypass list (no logging): `dex-architecture/`, `.claude/`, the hook script itself, `.git/`, `node_modules/`, `dist/`, `build/`, `.next/`.
