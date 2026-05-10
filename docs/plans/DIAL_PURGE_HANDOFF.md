# DIAL Purge — Coworker Handoff
**Last updated**: 2026-05-10  
**Branch**: work directly on `main` or open a new PR  
**Repo**: `cursedpotential/MCP_PLATFORM`

---

## What this is

Forensic evidence platform for an active custody case. It runs MCP tool servers, a React analyst UI, and PostgreSQL/DuckDB/Neo4j/LanceDB storage. It used to use AI DIAL (EPAM) as the gateway and chat UI. DIAL is fully deprecated and replaced — but ~60 files still have stale DIAL references that confuse every AI agent that reads them.

**Your job: find and replace every active DIAL reference with the correct current term.**

---

## What already got done

Previous work already handled:
- 7 DIAL-branded skill docs moved to `docs/wiki/archive/`
- Old DIAL planning docs moved to `_DEPRECATED/` at repo root
- New canonical root docs created: `GROUND_TRUTH.md`, `DECISION_REGISTER.md`, `PLATFORM_OVERVIEW.md`
- `AGENTS.md` partially updated

---

## Replacement glossary — use these exactly

| Old (wrong) | New (correct) |
|---|---|
| `AI DIAL Core` / `DIAL Core` | `ContextForge` |
| `AI DIAL` (as platform name) | `MCP Tool Platform` |
| `DIAL Chat` | `React + CopilotKit analyst UI` |
| `DIAL interceptor` | `ContextForge plugin` |
| `DIAL Auth Helper` | `Keycloak` |
| `DIAL_CORE_URL` env var | `CONTEXTFORGE_URL` |
| `AIDIAL_SETTINGS` | `ContextForge config` |

---

## Do NOT touch

- Anything under `_DEPRECATED/`
- Anything under `docs/wiki/archive/`
- Session transcripts: `docs/references/opencode-session-*.md`, `docs/references/session-summary-*.md`
- `DECISION_REGISTER.md` — documents DIAL as deprecated, that's intentional
- `docs/plans/DIAL_PURGE_HANDOFF.md` — this file

---

## Work list

### Group 1 — Do first (agents read these at session start)

AI agents read these first every session. Wrong info here corrupts everything downstream.

- `README.md` — still describes this as "AI DIAL stack"
- `PLATFORM_OVERVIEW.md` — new canonical doc but has remaining DIAL refs
- `PARITY_MATRIX.md` — references DIAL as current platform
- `.opencode/agents/platform.md` — primary agent instruction file
- `AGENTS.md` — root agent rules, partially updated
- `infrastructure/AGENTS.md` — infrastructure agent instructions

### Group 2 — Architecture and developer docs

- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/FAQ.md`
- `docs/architecture/TOOL_CATALOG.md`
- `docs/architecture/DATA_SOURCES.md`
- `docs/architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md`
- `docs/guides/DEVELOPMENT.md` — tells devs to run DIAL Core; needs ContextForge
- `docs/plans/ROADMAP.md`
- `docs/INDEX.md`
- `docs/wiki/INDEX.md`
- `docs/specs/SBV_INTEGRATION.md`
- `docs/specs/alpha1-inventory.md`

### Group 3 — Wiki skill and component docs (~35 files, bulk find-and-replace pass)

```
docs/wiki/project-docs/architecture/DATA_SOURCES.md
docs/wiki/project-docs/architecture/TOOL_CATALOG.md
docs/wiki/project-docs/architecture/mcp/protocol.md
docs/wiki/project-docs/components/frontend/copilotkit.md
docs/wiki/project-docs/components/frontend/react.md
docs/wiki/project-docs/components/infrastructure/caddy.md
docs/wiki/project-docs/components/infrastructure/docker-compose.md
docs/wiki/project-docs/components/infrastructure/dragonfly.md
docs/wiki/project-docs/components/orchestration/conductor/INDEX.md
docs/wiki/project-docs/components/orchestration/conductor/PLATFORM_IMPLEMENTATION.md
docs/wiki/project-docs/components/orchestration/contextforge/IMPLEMENTATION_ANALYSIS.md
docs/wiki/project-docs/components/orchestration/contextforge/INDEX.md
docs/wiki/project-docs/components/orchestration/contextforge/OVERVIEW.md
docs/wiki/project-docs/components/orchestration/contextforge/PROPOSED_ARCHITECTURE.md
docs/wiki/project-docs/components/security/keycloak.md
docs/wiki/project-docs/components/tools/scripts/README.md
docs/wiki/project-docs/components/utility/openrouter.md
docs/wiki/project-docs/proposals/haystack-incremental-parallel-deployment.md
docs/wiki/project-docs/references/external-tooling/haystack.md
docs/wiki/skills/database/postgresql.md
docs/wiki/skills/frontend/copilotkit.md
docs/wiki/skills/frontend/react.md
docs/wiki/skills/infrastructure/caddy.md
docs/wiki/skills/infrastructure/dragonfly.md
docs/wiki/skills/nlp/fastmcp.md
docs/wiki/skills/nlp/semantica.md
docs/wiki/skills/orchestration/conductor/INDEX.md
docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md
docs/wiki/skills/orchestration/contextforge/IMPLEMENTATION_ANALYSIS.md
docs/wiki/skills/orchestration/contextforge/PROPOSED_ARCHITECTURE.md
docs/wiki/skills/orchestration/mcp-protocol.md
docs/wiki/skills/orchestration/wundergraph-cosmo.md
docs/wiki/skills/security/keycloak.md
docs/wiki/skills/utility/openrouter.md
docs/wiki/tools/utility/README.md
```

### Group 4 — Source code (comments and description strings only — no logic changes)

- `mcp-servers/ts-mcp-server/src/index.ts` — "AI DIAL TypeScript MCP Server", "DIAL Core routes here" in comments
- `mcp-servers/ts-mcp-server/src/index.js` — same (compiled copy)
- `mcp-servers/js-mcp-server/src/index.js` — "AI DIAL JavaScript MCP Server", "DIAL Core and external"
- `mcp-servers/py-mcp-server/src/server.py` — "AI DIAL Python MCP Server" in module docstring and tool descriptions
- `mcp-servers/py-mcp-server/README.md`
- `mcp-servers/ts-mcp-server/README.md`

### Group 5 — Memory files (stale session state)

- `memory/MEMORY.md`
- `memory/MATT.md`
- `client/memory/MEMORY.md`
- `docs/memory/MEMORY.md`
- `mcp-servers/ts-mcp-server/memory/MEMORY.md`
- `mcp-servers/py-mcp-server/memory/MEMORY.md`
- `mcp-servers/js-mcp-server/memory/MEMORY.md`
- `mcp-servers/memory/MEMORY.md`
- `infrastructure/memory/MEMORY.md`

### Group 6 — Engineering decisions required (flag for Matt, do NOT touch without approval)

**`docker-compose.yml`** — running 5 EPAM images that need decisions:
- `epam/ai-dial-chat-themes` → DELETE (replaced by React app)
- `epam/ai-dial-chat` → DELETE
- `epam/ai-dial-core` → REPLACE with ContextForge container (needs image name from ContextForge docs)
- `epam/ai-dial-auth-helper` → DELETE (Keycloak handles auth directly per ADR-008)
- `epam/ai-dial-analytics-realtime` → no replacement planned — flag for Matt

Also: Keycloak realm named `dial`, DB user named `dial` — renaming is a breaking migration, separate decision needed.

**`infrastructure/interceptors/audit_logger/app.py`** — built as a DIAL interceptor using `DIAL_CORE_URL`. This is a **rewrite**, not a find-and-replace. Needs to become a ContextForge plugin using the `post_invoke` hook. Flag for Matt.

**`infrastructure/settings/settings.json`** — `AIDIAL_SETTINGS` config for DIAL Core. Gets deleted or replaced with ContextForge config when DIAL Core is removed from docker-compose. Flag for Matt.

---

## Verification

Run after completing Groups 1–5. Output should be empty:

```bash
grep -r "AI DIAL\|DIAL Core\|ai-dial-core\|epam/ai-dial\|DIAL Chat\|AIDIAL_SETTINGS\|DIAL_CORE_URL" \
  --include="*.md" --include="*.ts" --include="*.py" --include="*.js" \
  --include="*.json" --include="*.yaml" --include="*.yml" \
  . \
  | grep -v "_DEPRECATED\|/archive/\|DECISION_REGISTER\|DIAL_PURGE_HANDOFF\|node_modules\|opencode-session\|session-summary"
```

---

## Key files to read before editing anything

1. `GROUND_TRUTH.md` — authoritative platform state, read this first every session
2. `DECISION_REGISTER.md` — all 33 ADRs
3. `docs/wiki/skills/orchestration/contextforge/INDEX.md` — ContextForge architecture
4. `.opencode/agents/platform.md` — current agent definition (most up-to-date architecture view)
