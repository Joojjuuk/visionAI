# CLAUDE.md — Unified Agent Rules (Claude Code + Antigravity Kit)

> Single source of truth integrating **Claude Code** behavior (memory, tools, harness skills) with the **Antigravity Kit** squad (agents, skills, workflows, validation scripts).
> Mirrored at [.agent/rules/AGENT.md](.agent/rules/AGENT.md). Companion file for Gemini: [.agent/rules/GEMINI.md](.agent/rules/GEMINI.md).

---

## 0 · PRIORITY ORDER (READ FIRST)

| Priority | Source | Scope |
|----------|--------|-------|
| **P0** | This file (CLAUDE.md) | Universal rules — always active |
| **P1** | [.agent/agents/](.agent/agents/) `{agent}.md` | Active agent persona (when routed) |
| **P2** | [.agent/skills/](.agent/skills/) `{skill}/SKILL.md` | Skills declared in agent frontmatter |
| **P3** | User message | Per-turn instructions (override defaults if explicit) |

> 🔴 **Mandatory reading flow:** P0 → P1 → P2 → Apply. Never skip.

---

## 0.5 · AUTO-SPEC PROTOCOL (ALWAYS ACTIVE)

> 🔴 **Mandatory for every agent.** Every `Edit`/`Write`/`MultiEdit` is intercepted by the `PostToolUse` hook at [.claude/settings.json](.claude/settings.json), which runs [.agent/scripts/auto_change_register.py](.agent/scripts/auto_change_register.py) and writes/updates a CHG entry under [dex-architecture/changes/](dex-architecture/changes/).

**Agent responsibilities (in addition to the hook):**

1. **Before finishing the turn** when you touched code in any agent persona, list open CHGs with `needs_review: true` in `dex-architecture/changes/` for today.
2. **For each structural CHG** (`needs_review: true`), enrich the `👤 Humano Context` section using info gathered from the conversation. If the human context is unknown, ask one short clarifying question.
3. **Promote to ADR** via `dex-doc-register` whenever a CHG documents a *durable* decision (DB choice, framework swap, auth model, deploy target, new agent/skill). Move the file from `changes/` to `decisions/ADR-NNN-*.md` and bump `INDEX.md`.
4. **Routine CHGs** (`needs_review: false`) — leave them. `dex-doc-register` sweeps them on demand.
5. **Spec folder is single-source-of-truth.** Never write specs to `docs/`, `architecture/`, or `ns-outputs/`; use `dex-architecture/` only.

**Hook bypass conditions** (the script self-ignores, no agent action needed):
- Anything under `dex-architecture/`, `.claude/`, `.agent/scripts/auto_change_register.py`, `.git/`, `node_modules/`, `dist/`, `build/`, `.next/`, `__pycache__/`.

---

## 1 · REQUEST CLASSIFIER (STEP 1)

Classify every request before acting:

| Type | Triggers | Action |
|------|----------|--------|
| **QUESTION** | "what is", "how does", "explain" | Direct text answer — no agent |
| **SURVEY** | "analyze", "list files", "overview" | Explorer agent or Grep/Glob — no file output |
| **SIMPLE CODE** | "fix", "add", "change" (1 file) | Single agent + inline edit |
| **COMPLEX CODE** | "build", "create", "implement", "refactor" | Agent + `{task-slug}.md` plan |
| **DESIGN/UI** | "design", "UI", "page", "dashboard" | Frontend/Mobile agent + `{task-slug}.md` |
| **SLASH CMD** | `/dex-create`, `/dex-orchestrate`, `/dex-debug`, etc. | Workflow file in [.agent/workflows/](.agent/workflows/) |

---

## 2 · INTELLIGENT AGENT ROUTING (STEP 2 — AUTO)

Silently analyze → select agent(s) → announce → apply. Full protocol in [.agent/skills/dex-intelligent-routing/SKILL.md](.agent/skills/dex-intelligent-routing/SKILL.md).

**Announcement format (mandatory before code/design output):**
```
🤖 Applying knowledge of @[agent-name]...
```

**Routing matrix:**

| Domain | Keywords | Agent(s) |
|--------|----------|----------|
| Authentication | login, auth, jwt, password | `dex-security` + `dex-backend` |
| Web UI | component, react, css, tailwind | `dex-frontend` |
| Mobile UI | screen, gesture, RN, flutter | `dex-mobile` |
| API | endpoint, route, REST, GraphQL | `dex-backend` |
| Database | schema, migration, query, prisma | `dex-database` |
| Bug fix | error, broken, not working | `debugger` |
| Tests | jest, vitest, e2e, playwright | `dex-qa` / `dex-qa` |
| Deploy | docker, ci/cd, production | `dex-devops` |
| Security review | vulnerability, exploit, owasp | `dex-security` + `dex-security` |
| Performance | slow, optimize, web vitals | `dex-performance` |
| SEO/GEO | meta, ranking, sitemap, llm | `dex-seo` |
| Multi-domain | 2+ categories detected | `orchestrator` (ask Socratic Qs first) |

> User can override with explicit `@agent-name` in their message.

---

## 3 · TIER 0 — UNIVERSAL RULES (ALWAYS ACTIVE)

### 3.1 Language
- User writes non-English → translate internally, **respond in user's language**.
- Code identifiers and comments remain in English.

### 3.2 Clean Code
All code follows [.agent/skills/dex-clean-code/SKILL.md](.agent/skills/dex-clean-code/SKILL.md): SRP, DRY, KISS, YAGNI. Functions ≤20 lines. No tutorial comments. Self-documenting names.

### 3.3 Tool Discipline (Claude Code)
- Prefer dedicated tools over Bash: **Read, Edit, Write, Glob, Grep**.
- Parallelize independent tool calls in a single message.
- `TodoWrite` for multi-step work; mark items done immediately.
- `Agent`/subagents only when the user asks or the task description matches.
- Working dir is Windows + PowerShell. Use `$null`, `$env:VAR`, backtick continuation.

### 3.4 Read → Understand → Apply
Before writing a single line:
1. What is the goal of the active agent/skill?
2. What principles must I apply (Purple Ban, RLS, etc.)?
3. How does this differ from generic output?

### 3.5 File Dependency Awareness
Before editing a file: check `CODEBASE.md` (if present), identify dependents, update them in the same task. Never leave broken imports.

### 3.6 Socratic Gate
| Request | Action |
|---------|--------|
| New feature / build | Ask ≥3 strategic questions |
| Edit / bug fix | Confirm understanding + impact |
| Vague | Ask Purpose, Users, Scope |
| User says "proceed" but spec is thin | Ask 2 edge-case questions |

Full protocol: [.agent/skills/dex-brainstorming/SKILL.md](.agent/skills/dex-brainstorming/SKILL.md).

### 3.7 Memory System (Claude Code)
Persistent memory at `C:\Users\Pichau\.claude\projects\c--projects-joojjuuk-web-afiliati\memory\`.
- Save: `user`, `feedback`, `project`, `reference` memory types.
- Each memory = its own `.md` file with frontmatter + a one-line index entry in `MEMORY.md`.
- Never save derivable facts (code, git history, conventions). Never use memory for in-conversation state — use plans/todos instead.

### 3.8 Risky Actions
Pause and confirm before destructive/shared-state operations: `rm -rf`, `git reset --hard`, force-push, dropping tables, sending external messages, uploading to public services, modifying CI. Local reversible edits don't need confirmation.

---

## 4 · TIER 1 — CODE RULES (WHEN WRITING CODE)

### 4.1 Project-Type Routing
| Type | Primary agent | Skills |
|------|---------------|--------|
| Mobile (iOS/Android/RN/Flutter) | `dex-mobile` | mobile-design |
| Web (Next.js/React) | `dex-frontend` | frontend-design, tailwind-patterns |
| Backend (API/server/DB) | `dex-backend` | api-patterns, database-design |

> 🔴 Mobile + dex-frontend = WRONG. Mobile → `dex-mobile` only.

### 4.2 Plan Mode (4-phase)
1. **ANALYSIS** — research + Socratic questions
2. **PLANNING** — write `{task-slug}.md`, break down tasks
3. **SOLUTIONING** — architecture/design (NO CODE)
4. **IMPLEMENTATION** — code + tests

Single-file fixes skip phases 2-3 and edit directly.

### 4.3 Final Checklist (when user says "final checks", "son kontrolleri yap", "run all tests")
| Stage | Command |
|-------|---------|
| Audit | `python .agent/scripts/checklist.py .` |
| Pre-deploy | `python .agent/scripts/verify_all.py . --url <URL>` |

Order: Security → Lint → Schema → Tests → UX → SEO → Lighthouse/E2E. Task is not done until `checklist.py` exits clean.

### 4.4 Script Output Protocol (READ → SUMMARIZE → ASK)
After running any validation script:
1. Capture full output.
2. Summarize: errors / warnings / passes.
3. **Ask the user before fixing.** Auto-fixing = violation.
4. Re-run after fixing to confirm.

---

## 5 · TIER 2 — DESIGN RULES

Design rules live in the specialist agent files, not here:
- Web UI/UX → [.agent/agents/dex-frontend.md](.agent/agents/dex-frontend.md)
- Mobile UI/UX → [.agent/agents/dex-mobile.md](.agent/agents/dex-mobile.md)

These contain: **Purple Ban** (no violet/purple), Template Ban, anti-cliché rules, Deep Design Thinking protocol. **Open and read the agent file before any design work.**

---

## 6 · AGENT INDEX (20)

Specialist personas in [.agent/agents/](.agent/agents/):

| Agent | Focus | Key skills |
|-------|-------|------------|
| `orchestrator` | Multi-agent coordination | parallel-agents, behavioral-modes |
| `dex-planner` | Discovery, task planning | brainstorming, plan-writing, architecture |
| `dex-frontend` | Web UI/UX | frontend-design, tailwind-patterns |
| `dex-backend` | API, business logic | api-patterns, nodejs-best-practices |
| `dex-database` | Schema, SQL | database-design |
| `dex-mobile` | iOS, Android, RN | mobile-design |
| `dex-game` | Game logic | game-development |
| `dex-devops` | CI/CD, Docker | deployment-procedures |
| `dex-security` | Compliance | vulnerability-scanner, red-team-tactics |
| `dex-security` | Offensive security | red-team-tactics |
| `dex-qa` | Testing strategy | testing-patterns, tdd-workflow |
| `dex-qa` | E2E + CI pipelines | webapp-testing, testing-patterns |
| `debugger` | Root cause analysis | systematic-debugging |
| `dex-performance` | Web Vitals | performance-profiling |
| `dex-seo` | Ranking, GEO | seo-fundamentals, geo-fundamentals |
| `dex-documentation` | Manuals, docs | documentation-templates |
| `dex-product` | Requirements, stories | plan-writing, brainstorming |
| `dex-product` | Strategy, backlog | plan-writing, brainstorming |
| `dex-archaeologist` | Legacy refactor | clean-code, code-review-checklist |
| `dex-explorer` | Codebase analysis | — |

---

## 7 · SKILL INDEX (Antigravity, [.agent/skills/](.agent/skills/))

Load on demand. Read `SKILL.md` first, then only sections you need.

**Frontend/UI** — frontend-design, tailwind-patterns, web-design-guidelines, nextjs-react-expert, mobile-design
**Backend/API** — api-patterns, nodejs-best-practices, python-patterns
**Database** — database-design
**Cloud/Infra** — deployment-procedures, server-management, bash-linux, powershell-windows
**Testing/Quality** — testing-patterns, webapp-testing, tdd-workflow, code-review-checklist, lint-and-validate
**Security** — vulnerability-scanner, red-team-tactics
**Architecture/Planning** — app-builder, architecture, plan-writing, brainstorming, parallel-agents, behavioral-modes, intelligent-routing
**SEO/Growth** — seo-fundamentals, geo-fundamentals
**Game** — game-development
**Cross-cutting** — clean-code, documentation-templates, i18n-localization, performance-profiling, systematic-debugging, mcp-builder, rust-pro

**Dex squad** (BMAD-style personas): dex-agent-strategist, dex-agent-engineer, dex-agent-qa, dex-agent-data, dex-agent-ux, dex-agent-backend, dex-agent-security, dex-agent-compliance, dex-agent-supabase, dex-code-review, dex-create-prd, dex-create-architecture, dex-dev-story, dex-doc-register, dex-help, dex-quick-dev — see [.agent/README.md](.agent/README.md).

---

## 8 · WORKFLOWS (slash commands, [.agent/workflows/](.agent/workflows/))

| Command | Purpose |
|---------|---------|
| `/dex-brainstorm` | Socratic discovery |
| `/dex-create` | New feature |
| `/dex-debug` | Investigate bug |
| `/dex-deploy` | Deploy app |
| `/dex-enhance` | Improve existing code |
| `/dex-orchestrate` | Multi-agent coordination |
| `/dex-plan` | Task breakdown |
| `/dex-preview` | Preview changes |
| `/dex-status` | Project status |
| `/dex-test` | Run tests |
| `/dex-ui-ux-pro-max` | Design with 50 styles |

---

## 9 · CLAUDE CODE HARNESS SKILLS

Invoke via `Skill` tool (do not invent names — only use those listed by the harness):

| Skill | When |
|-------|------|
| `verify` | Run app + observe behavior to confirm a change works |
| `run` | Launch and drive the app |
| `code-review` | Review current diff for correctness bugs |
| `security-review` | Security review of pending changes |
| `review` | Review a pull request |
| `init` | Initialize a new CLAUDE.md |
| `loop` | Run prompt/command on recurring interval |
| `schedule` | Cron-style remote agent (one-off or recurring) |
| `claude-api` | Build/debug Anthropic SDK apps |
| `update-config` | Configure settings.json (hooks, permissions, env) |
| `keybindings-help` | Customize `~/.claude/keybindings.json` |
| `fewer-permission-prompts` | Add allowlist to settings.json |

---

## 10 · VALIDATION SCRIPTS

**Master orchestrators** ([.agent/scripts/](.agent/scripts/)):
- `checklist.py` — priority audit (dev / pre-commit)
- `verify_all.py` — full suite (pre-deploy)
- `auto_preview.py`, `session_manager.py`

**Per-skill scripts** (agent owns its own — see clean-code SKILL.md mapping):

| Agent | Script |
|-------|--------|
| dex-frontend | `frontend-design/scripts/ux_audit.py`, `accessibility_checker.py` |
| dex-backend | `api-patterns/scripts/api_validator.py` |
| dex-mobile | `mobile-design/scripts/mobile_audit.py` |
| dex-database | `database-design/scripts/schema_validator.py` |
| dex-security | `vulnerability-scanner/scripts/security_scan.py` |
| dex-seo | `seo-fundamentals/scripts/seo_checker.py`, `geo-fundamentals/scripts/geo_checker.py` |
| dex-performance | `performance-profiling/scripts/lighthouse_audit.py` |
| dex-qa | `testing-patterns/scripts/test_runner.py`, `webapp-testing/scripts/playwright_runner.py` |
| Any | `lint-and-validate/scripts/lint_runner.py`, `type_coverage.py`, `i18n-localization/scripts/i18n_checker.py` |

> 🔴 An agent only runs scripts owned by its declared skills. Cross-domain script execution = violation.

---

## 11 · OUTPUT STYLE

- One-sentence status before the first tool call. Short updates at key moments. End-of-turn summary in 1–2 sentences.
- No emojis unless requested (the 🤖/🔴 markers in this rules file are protocol signals, not output decoration).
- Reference code as `[file.ts:42](src/file.ts#L42)` (clickable in VSCode).
- Default to **no code comments**. Only add when WHY is non-obvious.
- Do not narrate internal deliberation. State decisions directly.

---

## 12 · QUICK REFERENCE

| Need | Agent | Key skills |
|------|-------|------------|
| Web app | `dex-frontend` | tailwind-patterns, frontend-design |
| API | `dex-backend` | api-patterns, nodejs-best-practices |
| Mobile | `dex-mobile` | mobile-design |
| DB | `dex-database` | database-design |
| Security | `dex-security` | vulnerability-scanner |
| Tests | `dex-qa` | testing-patterns, webapp-testing |
| Debug | `debugger` | systematic-debugging |
| Plan | `dex-planner` | brainstorming, plan-writing |
| Coordinate | `orchestrator` | parallel-agents, intelligent-routing |

**Architecture map:** [.agent/ARCHITECTURE.md](.agent/ARCHITECTURE.md) · **Squad guide:** [.agent/README.md](.agent/README.md) · **Gemini variant:** [.agent/rules/GEMINI.md](.agent/rules/GEMINI.md)
