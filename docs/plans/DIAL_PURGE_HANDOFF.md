# DIAL Purge & Branch Merge Handoff
**Date**: 2026-05-10  
**Branch**: `claude/compare-codebases-pVur6` (currently identical to `main` — no divergence)  
**Priority**: Documentation sprint before next code work begins  
**Assigned to**: Docs coworker

---

## Context

AI DIAL (EPAM) was the original gateway and chat UI for this platform. It has been fully deprecated:

| Deprecated Component | Replacement | ADR |
|---|---|---|
| DIAL Core (gateway) | ContextForge (IBM MCP Gateway) | ADR-031 |
| DIAL Chat (UI) | React + CopilotKit (analyst UI) | — |
| DIAL Auth Helper | Keycloak direct (ADR-008) | ADR-008 |
| DIAL interceptors | ContextForge plugin pipeline | ADR-031 |
| Agno orchestrator | Conductor OSS | ADR-033 |
| n8n | Conductor OSS | ADR-033 |

DIAL references are still scattered across ~70 files. This causes confusion for every agent and developer reading the docs. **All active docs must reflect the current architecture.** Historical session transcripts and archived plans are exempt — leave those alone.

---

## Branch Situation

Both `main` and `claude/compare-codebases-pVur6` are identical — no commits separate them. 

**Do all work on `claude/compare-codebases-pVur6`.** When complete, open a PR into `main`.

---

## Work Categories

### Category A — DELETE or ARCHIVE (DIAL-specific, no longer relevant)

These files document DIAL itself as a product. They are not historical transcripts — they are active skill/component docs that will actively mislead agents. Move them to `docs/archive/`.

Archive path convention: `docs/archive/<same-relative-path-from-repo-root>`

| File to Archive | Reason |
|---|---|
| `docs/wiki/skills/dial-codebase-analysis/SKILL.md` | Skill for analyzing DIAL codebase — irrelevant |
| `docs/wiki/skills/infrastructure/AI_DIAL_EXPERT.md` | DIAL expert persona skill — irrelevant |
| `docs/wiki/skills/infrastructure/ai-dial-core.md` | DIAL Core skill reference — replaced by ContextForge |
| `docs/wiki/skills/frontend/dial-chat.md` | DIAL Chat skill — UI is now React + CopilotKit |
| `docs/wiki/project-docs/components/infrastructure/AI_DIAL_EXPERT.md` | Same as above, project-docs mirror |
| `docs/wiki/project-docs/components/infrastructure/ai-dial-core.md` | Same — DIAL Core component doc |
| `docs/wiki/project-docs/components/frontend/dial-chat.md` | Same — DIAL Chat component doc |

After archiving, remove any index links to these files from `docs/INDEX.md` and relevant `README.md` files.

---

### Category B — UPDATE (active docs with DIAL references to replace)

These are live, authoritative docs that agents read. Every DIAL reference needs to become the correct replacement term.

**Replacement glossary:**
- `AI DIAL Core` / `DIAL Core` → `ContextForge (IBM MCP Gateway)`
- `DIAL Chat` → `React + CopilotKit analyst UI` (or just `HITL analyst UI`)
- `DIAL interceptor` → `ContextForge plugin`
- `DIAL Auth Helper` → `Keycloak` (direct, no helper proxy)
- `AI DIAL` (as platform name) → `MCP Tool Platform` or `the platform`
- `epam/ai-dial-*` Docker images → mark as deprecated / note replacement
- `DIAL_CORE_URL` env var → `CONTEXTFORGE_URL` (verify actual env var name in ContextForge docs)
- `AIDIAL_SETTINGS` → ContextForge config (check `docs/wiki/skills/orchestration/contextforge/`)
- Port `:8080` labeled as "DIAL Core" → ContextForge now owns this port (Conductor will use it too — confirm)

**Files to update:**

| File | What to change |
|---|---|
| `AGENTS.md` | Architecture section references DIAL — update to ContextForge + Conductor |
| `README.md` | Project description still mentions AI DIAL stack |
| `docs/INDEX.md` | Remove links to archived files; update architecture overview |
| `docs/architecture/ARCHITECTURE.md` | Full architecture doc — comprehensive DIAL→ContextForge pass |
| `docs/architecture/FAQ.md` | Q&A may reference DIAL as current |
| `docs/architecture/STORIES.md` | User stories framed around DIAL surfaces |
| `docs/architecture/TOOL_CATALOG.md` | Tool catalog may reference DIAL routing |
| `docs/architecture/DATA_SOURCES.md` | Data source routing references |
| `docs/dependencies/DEPENDENCY_GRAPH.md` | DIAL appears in dependency graph |
| `docs/guides/DEVELOPMENT.md` | Dev setup likely tells devs to run DIAL Core |
| `docs/plans/ROADMAP.md` | Roadmap may have DIAL milestones that are now obsolete |
| `docs/wiki/project-docs/architecture/ARCHITECTURE.md` | Mirror of main architecture doc |
| `docs/wiki/project-docs/architecture/TOOL_CATALOG.md` | Mirror |
| `docs/wiki/project-docs/architecture/DATA_SOURCES.md` | Mirror |
| `docs/wiki/project-docs/architecture/mcp/protocol.md` | MCP protocol framed against DIAL |
| `docs/wiki/project-docs/components/frontend/copilotkit.md` | May reference DIAL as host |
| `docs/wiki/project-docs/components/frontend/react.md` | React app framed against DIAL |
| `docs/wiki/project-docs/components/infrastructure/caddy.md` | Caddy proxying DIAL Core |
| `docs/wiki/project-docs/components/infrastructure/docker-compose.md` | References DIAL services |
| `docs/wiki/project-docs/components/infrastructure/dragonfly.md` | Dragonfly used by DIAL Redis |
| `docs/wiki/project-docs/components/orchestration/contextforge/INDEX.md` | May still mention DIAL as predecessor |
| `docs/wiki/project-docs/components/orchestration/contextforge/OVERVIEW.md` | Same |
| `docs/wiki/project-docs/components/orchestration/contextforge/IMPLEMENTATION_ANALYSIS.md` | Same |
| `docs/wiki/project-docs/components/orchestration/contextforge/PROPOSED_ARCHITECTURE.md` | Same |
| `docs/wiki/project-docs/components/security/keycloak.md` | Keycloak integrated via DIAL realm — realm name may have changed |
| `docs/wiki/project-docs/components/tools/scripts/README.md` | Script docs |
| `docs/wiki/project-docs/components/tools/scripts/chatgpt_parser.md` | May reference DIAL |
| `docs/wiki/project-docs/components/utility/openrouter.md` | OpenRouter referenced as DIAL alternative |
| `docs/wiki/project-docs/proposals/haystack-incremental-parallel-deployment.md` | Proposal framed against DIAL |
| `docs/wiki/project-docs/references/external-tooling/haystack.md` | Same |
| `docs/wiki/skills/database/lancedb.md` | Skill may reference DIAL context |
| `docs/wiki/skills/database/neo4j.md` | Same |
| `docs/wiki/skills/database/postgresql.md` | Same |
| `docs/wiki/skills/frontend/copilotkit.md` | May reference DIAL |
| `docs/wiki/skills/frontend/react.md` | Same |
| `docs/wiki/skills/infrastructure/caddy.md` | Caddy skill references DIAL routing |
| `docs/wiki/skills/infrastructure/docker-compose.md` | docker-compose skill |
| `docs/wiki/skills/infrastructure/dragonfly.md` | Same |
| `docs/wiki/skills/nlp/fastmcp.md` | May reference DIAL as host |
| `docs/wiki/skills/nlp/semantica.md` | Same |
| `docs/wiki/skills/orchestration/contextforge/IMPLEMENTATION_ANALYSIS.md` | Contextforge skills docs |
| `docs/wiki/skills/orchestration/contextforge/PROPOSED_ARCHITECTURE.md` | Same |
| `docs/wiki/skills/orchestration/mcp-protocol.md` | MCP protocol framed against DIAL |
| `docs/wiki/skills/orchestration/wundergraph-cosmo.md` | WunderGraph framed as DIAL component |
| `docs/wiki/skills/security/keycloak.md` | Keycloak skill references DIAL realm |
| `docs/wiki/skills/utility/openrouter.md` | Same |
| `docs/wiki/tools/legacy/mcp-tool-platform-porting-guide.md` | Porting guide may reference DIAL target |
| `docs/wiki/tools/utility/README.md` | Same |
| `docs/wiki/tools/utility/chatgpt_parser.md` | Same |
| `memory/MEMORY.md` | Session memory may have stale DIAL state |
| `infrastructure/AGENTS.md` | Infrastructure agent instructions reference DIAL |

---

### Category C — DO NOT TOUCH (historical transcripts — leave as-is)

These are session transcripts and historical records. DIAL references in them are accurate for the time they were written. Do not update them.

```
docs/references/opencode-session-2026-03-15-session2-architecture.md
docs/references/opencode-session-2026-03-15-transcript-summary.md
docs/references/session-summary-2026-03-31.md
docs/wiki/project-docs/references/opencode-session-2026-03-15-*.md
docs/wiki/archive/**
docs/archive/**
docs/archive/wiki/plannotator-noncanonical-2026-04-08/**
```

---

### Category D — SOURCE CODE FIXES (comments and strings only — no logic changes)

These source files have DIAL in comments, docstrings, or description strings. The logic is fine — just update the labels.

| File | What to change |
|---|---|
| `mcp-servers/ts-mcp-server/src/index.ts` | Lines 18-23: "AI DIAL TypeScript MCP Server", "AI DIAL Core can", "DIAL compatibility" → ContextForge |
| `mcp-servers/ts-mcp-server/src/index.ts` | Line 69: ping description "running within DIAL" → "running" |
| `mcp-servers/ts-mcp-server/src/index.ts` | Line 398: "DIAL Core routes here" → "ContextForge routes here" |
| `mcp-servers/ts-mcp-server/src/index.js` | Same as index.ts (compiled copy — update source, rebuild) |
| `mcp-servers/js-mcp-server/src/index.js` | Lines 10-29: "AI DIAL JavaScript MCP Server", "DIAL Core and external" → ContextForge |
| `mcp-servers/py-mcp-server/src/server.py` | Lines 2, 45, 153: "AI DIAL Python MCP Server", "DIAL" in description strings |

---

### Category E — REARCHITECT (requires engineering judgment — flag for Matt)

These files are not just doc updates — they have structural DIAL dependencies that need design decisions.

#### `docker-compose.yml` — Full DIAL stack replacement needed

Currently runs 5 EPAM Docker images that no longer belong:
- `epam/ai-dial-chat-themes:0.9.1` → DELETE (DIAL Chat replaced by React app)
- `epam/ai-dial-chat:0.26.0` → DELETE
- `epam/ai-dial-core:0.25.1` → REPLACE with ContextForge container (check ContextForge docs for image)
- `epam/ai-dial-auth-helper:0.6.2` → DELETE (Keycloak handles auth directly via ADR-008)
- `epam/ai-dial-analytics-realtime:0.6.2` → DECISION NEEDED (no replacement planned yet)

Also: Keycloak realm is named `dial` and DB user is `dial`. These should be renamed (breaking change — requires migration).

**Do not make these changes without Matt's explicit approval.** Flag this block as a separate task.

#### `infrastructure/settings/settings.json`

This is `AIDIAL_SETTINGS` — the DIAL Core configuration file. It references the `dial` Keycloak realm. Once DIAL Core is removed, this file either:
- Gets replaced by ContextForge configuration (different format entirely), OR
- Gets deleted

**Flag for Matt before touching.**

#### `infrastructure/interceptors/audit_logger/app.py`

This is built as a **DIAL interceptor** — it hooks into DIAL Core's middleware pipeline (`DIAL_CORE_URL` env var, proxies requests through DIAL). With DIAL Core gone, this architecture doesn't work.

The audit logger needs to become a **ContextForge plugin** instead. ContextForge has a `post_invoke` plugin hook that is the correct integration point. This is a rewrite, not a find-and-replace.

**Flag for Matt before touching.**

---

## Completion Checklist

- [ ] Branch: all work on `claude/compare-codebases-pVur6`
- [ ] Category A: 7 DIAL skill/component docs archived to `docs/archive/`
- [ ] Category A: `docs/INDEX.md` updated to remove archived file links
- [ ] Category B: All ~45 active docs updated — no remaining `DIAL Core`, `AI DIAL`, `DIAL Chat` in active guidance
- [ ] Category B: Replacement glossary applied consistently across all files
- [ ] Category C: Historical transcripts untouched
- [ ] Category D: 6 source files updated (comments/strings only, no logic)
- [ ] Category E: Flagged and documented for Matt — do not attempt without approval
- [ ] Run `grep -r "AI DIAL\|DIAL Core\|DIAL Chat\|ai-dial-core\|ai-dial-chat\|epam/ai-dial" --include="*.md" --include="*.ts" --include="*.py" --include="*.js" docs/ mcp-servers/ AGENTS.md README.md | grep -v "docs/archive\|docs/references\|deprecated\|was replaced\|formerly"` and verify output is empty or only in legitimate historical context
- [ ] Commit with message: `docs: purge DIAL references, update to ContextForge + Conductor architecture`
- [ ] Push to `claude/compare-codebases-pVur6`
- [ ] Open PR into `main` — title: "Docs: Complete DIAL deprecation purge"

---

## Key Reference Files

Before editing any file, read these to understand the correct current architecture:

1. `GROUND_TRUTH.md` — authoritative platform state (read this first, every time)
2. `DECISION_REGISTER.md` — all 33 ADRs
3. `docs/wiki/skills/orchestration/contextforge/INDEX.md` — ContextForge architecture
4. `docs/wiki/skills/orchestration/conductor/SKILL.md` — Conductor OSS reference
5. `.opencode/agents/platform.md` — current agent definition (most up-to-date architecture view)

---

## What "Done" Looks Like

An AI agent reading any active doc in this repo should be able to correctly answer:
- "What is the MCP gateway?" → ContextForge (IBM)
- "What replaced DIAL Core?" → ContextForge
- "What is the orchestrator?" → Conductor OSS (not yet deployed — GATE LOCKED)
- "What is the analyst UI?" → React + CopilotKit
- "What runs the auth?" → Keycloak directly

If the agent would answer "DIAL" to any of these, the purge is incomplete.
