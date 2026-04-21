---
title: Conductor OSS — Wiki Index
type: index
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - orchestration
  - workflow
  - ai-agents
  - mcp
  - orkes
adr: ADR-033
---

# Conductor OSS — Wiki Index

Conductor OSS is the single orchestration and AI agent execution layer for MCP_PLATFORM. It replaced both Agno (agent runtime) and n8n (low-code automation) per ADR-033.

## Files in This Directory

| File | Contents |
|------|----------|
| [OVERVIEW.md](OVERVIEW.md) | Platform role, ADR-033 rationale, CONDUCTOR GATE, architecture position |
| [OSS_REFERENCE.md](OSS_REFERENCE.md) | Conductor OSS engine — task types, AI tasks, MCP integration, SDKs, CLI, Docker |
| [ORKES_REFERENCE.md](ORKES_REFERENCE.md) | Orkes Conductor — enterprise features, cloud, schedules, secrets, webhooks |
| [PLATFORM_IMPLEMENTATION.md](PLATFORM_IMPLEMENTATION.md) | How MCP_PLATFORM uses Conductor — worker patterns, HUMAN task bridge, integration plan |
| [ECOSYSTEM.md](ECOSYSTEM.md) | MCP server, Claude plugin, Anti-Gravity, AI cookbook, tutorials, community examples |

## Quick Facts

- **License**: Apache 2.0
- **Server port**: 8080 (UI + API)
- **Replaces**: Agno (ADR-033), n8n (ADR-033)
- **Gate**: CONDUCTOR GATE — no Conductor integration merged until first end-to-end ingest test passes
- **LLM providers**: 14+ native
- **SDKs**: Java, Python, JavaScript/TypeScript, Go, C#, Ruby, Rust
- **MCP**: `LIST_MCP_TOOLS` + `CALL_MCP_TOOL` native task types

## Related Wiki Entries

- [[skills/orchestration/contextforge/INDEX|ContextForge]] — MCP gateway (ADR-031)
- [[skills/nlp/semantica|Semantica]] — forensic NLP engine (py-mcp-server)
- [[skills/infrastructure/docker-compose|Docker Compose]]
- [[INDEX|Wiki Index]]

## Archived Entries

The following were deprecated per ADR-033 and moved to archive:
- `docs/wiki/archive/skills/infrastructure/ai-dial-core.md`
- `docs/wiki/archive/skills/infrastructure/AI_DIAL_EXPERT.md`
- `docs/wiki/archive/skills/frontend/dial-chat.md`
- `docs/wiki/archive/skills/dial-codebase-analysis/SKILL.md`
