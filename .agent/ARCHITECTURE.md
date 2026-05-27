# Antigravity Kit Architecture (Unified — DEX namespace)

> AI Agent Capability Expansion Toolkit. All artifacts use the **`dex-*`** namespace after the 2026-05-24 consolidation.

---

## 📋 Overview

- **20 Specialist Agents** (all `dex-*`)
- **37 Skills** (all `dex-*`)
- **11 Workflows** (all `/dex-*`)
- **Auto-spec system** in [../dex-architecture/](../dex-architecture/) — every Edit/Write produces a CHG entry via [.claude/settings.json](../.claude/settings.json) hook running [scripts/auto_change_register.py](scripts/auto_change_register.py)

---

## 🏗️ Directory Structure

```plaintext
.agent/
├── ARCHITECTURE.md          # This file
├── README.md                # Squad guide
├── agents/                  # 20 dex-* specialist agents
├── skills/                  # 37 dex-* skill modules
├── workflows/               # 11 /dex-* slash commands
├── rules/                   # AGENT.md (mirror of /CLAUDE.md) + GEMINI.md
└── scripts/                 # Master validation + auto-spec hook
    ├── auto_change_register.py  # PostToolUse hook target
    ├── checklist.py
    ├── verify_all.py
    ├── auto_preview.py
    └── session_manager.py

dex-architecture/            # Auto-maintained spec folder
├── INDEX.md
├── decisions/   (ADR)
├── solutions/   (SOL)
├── changes/     (CHG — auto)
└── standards/   (STD)

.claude/
└── settings.json            # PostToolUse → auto_change_register.py
```

---

## 🤖 Agents (20)

| Agent | Focus | Source of merge | Key skills |
|-------|-------|-----------------|------------|
| `dex-orchestrator` | Multi-agent coordination | orchestrator | dex-parallel-agents, dex-behavioral-modes |
| `dex-planner` | Discovery, task planning | project-planner | dex-brainstorming, dex-plan-writing, dex-system-design |
| `dex-product` | PRD + backlog + strategy | product-manager + product-owner + dex-agent-strategist (Ana) | dex-plan-writing, dex-brainstorming, dex-create-prd |
| `dex-frontend` | Web UI implementation | frontend-specialist | dex-frontend-design |
| `dex-ux` | Design persona | dex-agent-ux (Maya) | dex-frontend-design |
| `dex-backend` | API + server systems | backend-specialist + dex-agent-backend (Kai) | dex-api-patterns, dex-nodejs, dex-python, dex-database-design |
| `dex-database` | Schema, RLS, Postgres/Supabase | database-architect + dex-agent-supabase (Viktor) | dex-database-design |
| `dex-mobile` | iOS/Android/RN | mobile-developer | dex-mobile-design |
| `dex-game` | Game logic, mechanics | game-developer | dex-game-development |
| `dex-devops` | CI/CD, Docker | devops-engineer | dex-deployment |
| `dex-security` | Defensive + offensive security | security-auditor + penetration-tester + dex-agent-security (Rex) | dex-security-scan |
| `dex-qa` | Tests + automation + release gate | test-engineer + qa-automation-engineer + dex-agent-qa (Luna) | dex-testing, dex-code-review, dex-lint |
| `dex-debugger` | Root cause analysis | debugger | dex-systematic-debugging |
| `dex-performance` | Web Vitals, profiling | performance-optimizer | dex-performance-profiling |
| `dex-seo` | SEO + GEO | seo-specialist | dex-seo-fundamentals, dex-geo-fundamentals |
| `dex-documentation` | Manuals, docs | documentation-writer | dex-documentation-templates |
| `dex-archaeologist` | Legacy refactor | code-archaeologist | dex-clean-code, dex-code-review |
| `dex-explorer` | Codebase analysis | explorer-agent | — |
| `dex-data` | Data analyst | dex-agent-data (Iris) | — |
| `dex-compliance` | Regulatory / privacy | dex-agent-compliance | — |

---

## 🧩 Skills (37)

Load on demand. Progressive disclosure — read SKILL.md first, then sub-sections.

### Frontend / UI
| Skill | Notes |
|-------|-------|
| `dex-frontend-design` | **Merged**: frontend-design + web-design-guidelines (Vercel 100+) + tailwind-patterns (TW v4) + nextjs-react-expert (Vercel 57 perf) |
| `dex-mobile-design` | Mobile UI patterns |

### Backend / API
| Skill | Notes |
|-------|-------|
| `dex-api-patterns` | REST, GraphQL, tRPC |
| `dex-nodejs` | Node.js async, modules |
| `dex-python` | FastAPI, Pydantic v2 |
| `dex-rust` | Rust patterns |
| `dex-database-design` | Schema, indexing |

### Architecture & Planning
| `dex-system-design` | System design patterns |
| `dex-app-builder` | Full-stack scaffolding |
| `dex-plan-writing` | Task planning |
| `dex-brainstorming` | Socratic questioning |
| `dex-intelligent-routing` | Auto agent selection |
| `dex-behavioral-modes` | Modes (brainstorm/implement/etc) |
| `dex-parallel-agents` | Multi-agent orchestration |

### Testing & Quality
| `dex-testing` | **Merged**: testing-patterns + webapp-testing + tdd-workflow |
| `dex-code-review` | **Merged**: dex-code-review + code-review-checklist |
| `dex-lint` | Lint + validation |

### Security
| `dex-security-scan` | **Merged**: vulnerability-scanner + red-team-tactics |

### Cloud / Infra
| `dex-deployment` | CI/CD, deploy procedures |
| `dex-server-management` | Infra management |
| `dex-shell-bash` | Linux shell scripting |
| `dex-shell-powershell` | Windows PowerShell |

### Debug & Perf
| `dex-systematic-debugging` | Root cause analysis |
| `dex-performance-profiling` | Web Vitals, profiling |

### SEO
| `dex-seo-fundamentals` | E-E-A-T, Core Web Vitals |
| `dex-geo-fundamentals` | LLM/GenAI optimization |

### Cross-cutting
| `dex-clean-code` | Coding standards (P0) |
| `dex-documentation-templates` | Doc formats |
| `dex-i18n` | Internationalization |
| `dex-mcp-builder` | Model Context Protocol |
| `dex-game-development` | Game logic |

### DEX workflow skills (kept as-is)
| `dex-create-prd` | Guided PRD creation |
| `dex-create-architecture` | C4 model architecture |
| `dex-dev-story` | Rigorous story implementation |
| `dex-doc-register` | ADR/SOL/CHG/STD registry — **integrates with auto-trigger** |
| `dex-quick-dev` | Clarify→Plan→Build→Review fast loop |
| `dex-help` | Project guide |
| `dex-skills-guide` | How to build skills (was `doc.md`) |

---

## 🔄 Workflows (11) — `/dex-*`

| Command | Purpose |
|---------|---------|
| `/dex-brainstorm` | Socratic discovery |
| `/dex-create` | Create new feature |
| `/dex-debug` | Debug issue |
| `/dex-deploy` | Deploy application |
| `/dex-enhance` | Improve existing code |
| `/dex-orchestrate` | Multi-agent coordination |
| `/dex-plan` | Task breakdown |
| `/dex-preview` | Preview changes |
| `/dex-status` | Project status |
| `/dex-test` | Run tests |
| `/dex-ui-ux-pro-max` | Design with 50 styles |

---

## 🎯 Auto-Spec System (NEW)

Every `Edit`/`Write`/`MultiEdit` automatically triggers [scripts/auto_change_register.py](scripts/auto_change_register.py) (via `PostToolUse` hook in [.claude/settings.json](../.claude/settings.json)), which appends/updates a `CHG-YYYYMMDD-<component>.md` in [../dex-architecture/changes/](../dex-architecture/changes/) and flags structural changes for ADR upgrade.

| Change type | Outcome |
|-------------|---------|
| Agent/skill/workflow edit | `agent-config` CHG, `needs_review: true` |
| `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` | `dependencies` CHG, `needs_review: true` |
| Migrations, `schema.prisma`, `*.sql` | `database` CHG, `needs_review: true` |
| `api/`, `routes/`, `app/api/` | `api-surface` CHG, `needs_review: true` |
| `Dockerfile`, `docker-compose*`, `*.tf` | `infrastructure` CHG, `needs_review: true` |
| `.github/workflows/*` | `ci-cd` CHG, `needs_review: true` |
| `CLAUDE.md`, `AGENT.md`, `GEMINI.md`, `ARCHITECTURE.md` | `agent-rules` CHG, `needs_review: true` |
| Anything else under src/, lib/, etc | routine CHG (`needs_review: false`) |

Agents must read open `needs_review: true` CHGs before finishing the turn, enrich the `👤 Humano Context`, and promote to ADR via `dex-doc-register` when applicable.

---

## 📊 Master Validation Scripts

| Script | Purpose | When |
|--------|---------|------|
| `scripts/checklist.py` | Priority-based audit | Dev / pre-commit |
| `scripts/verify_all.py` | Full comprehensive suite | Pre-deploy |
| `scripts/auto_change_register.py` | **PostToolUse hook target** | Every Edit/Write (automatic) |
| `scripts/auto_preview.py` | Preview pipeline | On demand |
| `scripts/session_manager.py` | Session orchestration | On demand |

Usage:
```bash
py .agent/scripts/checklist.py .
py .agent/scripts/verify_all.py . --url http://localhost:3000
```

---

## 🔗 Quick Reference

| Need | Agent | Top skills |
|------|-------|-----------|
| Web App | `dex-frontend` | dex-frontend-design |
| API | `dex-backend` | dex-api-patterns, dex-nodejs |
| Mobile | `dex-mobile` | dex-mobile-design |
| Database | `dex-database` | dex-database-design |
| Security | `dex-security` | dex-security-scan |
| Testing | `dex-qa` | dex-testing |
| Debug | `dex-debugger` | dex-systematic-debugging |
| Plan | `dex-planner` | dex-brainstorming, dex-plan-writing |
| Product | `dex-product` | dex-create-prd, dex-plan-writing |
| Coordinate | `dex-orchestrator` | dex-parallel-agents |
