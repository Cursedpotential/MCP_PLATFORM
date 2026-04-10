# TASK: Update Documentation Path References After Restructure

**Priority:** Low — grunt work, use cheapest model available
**Scope:** ONLY fix path references in docs. Do NOT rewrite content.

## What Changed (already done — do NOT move files)

| Old Path | New Path |
|----------|----------|
| `ts-mcp-server/` | `mcp-servers/ts-mcp-server/` |
| `py-mcp-server/` | `mcp-servers/py-mcp-server/` |
| `js-mcp-server/` | `mcp-servers/js-mcp-server/` |
| `core/` | `infrastructure/core/` |
| `settings/` | `infrastructure/settings/` |
| `init/` | `infrastructure/init/` |
| `Caddyfile` | `infrastructure/Caddyfile` |
| `interceptors/` | `infrastructure/interceptors/` |

docker-compose.yml is ALREADY updated. Do NOT touch it.

## Files to Update

1. `docs/ARCHITECTURE.md` — Update directory tree + all path refs
2. `CLAUDE.md` — Fix any old path references
3. `README.md` — Fix any old path references  
4. `docs/ROADMAP.md` — Fix any old path references
5. `docs/TOOL_CATALOG.md` — Fix any old path references
6. `docs/DATA_SOURCES.md` — Fix any old path references
7. CREATE `docs/references/restructure-2026-03-16.md` documenting moves

## Rules
- ONLY update path references
- Do NOT rewrite content, add features, or change descriptions
- Do NOT touch docker-compose.yml or any source code
- Do NOT add dependencies or restructure anything
