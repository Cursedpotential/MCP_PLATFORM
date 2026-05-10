# _DEPRECATED — Superseded Documents

> **Matt's review queue.** Nothing in this directory is deleted — it is waiting for Matt to review and permanently remove when ready.
> **Agents**: Do not read files in this directory as authoritative. They contain stale information. Read `GROUND_TRUTH.md` instead.

## Why these documents were moved

All files here were written before one or more of the following events:
- DIAL Core deprecated (not running, not the gateway)
- ADR-033: Conductor OSS replaces Agno and n8n (2026-04-21)
- ORCHESTRATION_CONTRACT.md established as the agent governance document (2026-04-21)
- MCP_PLATFORM_SYSTEM_PROMPT_V3.md superseded V2 (2026-04-21)

## Mirror structure

Files are stored here mirroring their original repo path:

| Original path | Archived at |
|---|---|
| `POST_DIAL_MASTER_OVERVIEW.md` | `_DEPRECATED/root/POST_DIAL_MASTER_OVERVIEW.md` |
| `SPRINT_PLAN.md` | `_DEPRECATED/root/SPRINT_PLAN.md` |
| `POST_DIAL_REPLACEMENT_ARCHITECTURE.md` | `_DEPRECATED/root/POST_DIAL_REPLACEMENT_ARCHITECTURE.md` |
| `IMPLEMENTATION_PHASE_PLAN.md` | `_DEPRECATED/root/IMPLEMENTATION_PHASE_PLAN.md` |
| `AGENT_HANDOFF_PROMPT_POST_DIAL.md` | `_DEPRECATED/root/AGENT_HANDOFF_PROMPT_POST_DIAL.md` |
| `MCP_PLATFORM_SYSTEM_PROMPT_V2.md` | `_DEPRECATED/root/MCP_PLATFORM_SYSTEM_PROMPT_V2.md` |
| `docs/architecture/TOOL_CATALOG.md` | `_DEPRECATED/docs/architecture/TOOL_CATALOG.md` |
| `docs/architecture/DATA_SOURCES.md` | `_DEPRECATED/docs/architecture/DATA_SOURCES.md` |
| `infrastructure/core/prompts/INGESTION_AGENT_PROMPT.md` | `_DEPRECATED/infrastructure/core/prompts/INGESTION_AGENT_PROMPT.md` |

## How to permanently delete

When Matt is ready to remove a file permanently:
```bash
git rm _DEPRECATED/root/FILENAME.md
git commit -m "cleanup: permanently remove deprecated FILENAME.md"
```
