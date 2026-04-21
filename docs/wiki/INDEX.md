---
title: Wiki Index
reviewed: 2026-04-21
revision: 3
author: Computer
status: current
---

# Wiki Index

## Overview

This wiki is the reference layer over the MCP_PLATFORM documentation tree. All active architecture and skill entries are grounded in the actual codebase. Stale or superseded entries are moved to `docs/wiki/archive/` with full content preserved.

## Quick Navigation

### Architecture & Platform

- [GROUND_TRUTH.md](/GROUND_TRUTH.md) — authoritative platform state: what runs, what is deprecated, what is planned
- [MCP_PLATFORM_SYSTEM_PROMPT_V3.md](/MCP_PLATFORM_SYSTEM_PROMPT_V3.md) — current system prompt for development agents
- [ORCHESTRATION_CONTRACT.md](/ORCHESTRATION_CONTRACT.md) — agent governance: change gates, approval protocol, no-stubs rule
- [DECISION_REGISTER_POST_DIAL.md](/DECISION_REGISTER_POST_DIAL.md) — ADRs including ADR-031 (ContextForge), ADR-033 (Conductor replaces Agno+n8n)
- [INDEX.md](/INDEX.md) — root index

### Orchestration

- [Conductor OSS — Index](skills/orchestration/conductor/INDEX.md) — **CURRENT** — ADR-033
  - [OVERVIEW](skills/orchestration/conductor/OVERVIEW.md) — platform role, CONDUCTOR GATE, open questions
  - [OSS_REFERENCE](skills/orchestration/conductor/OSS_REFERENCE.md) — task types, AI tasks, CLI, Docker, SDKs
  - [ORKES_REFERENCE](skills/orchestration/conductor/ORKES_REFERENCE.md) — enterprise features, cloud, MCP server config
  - [PLATFORM_IMPLEMENTATION](skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md) — worker patterns, HUMAN task bridge (OQ-C5), deployment
  - [ECOSYSTEM](skills/orchestration/conductor/ECOSYSTEM.md) — MCP server, Claude plugin, Anti-Gravity, AI cookbook, tutorials
- [ContextForge — Index](skills/orchestration/contextforge/INDEX.md) — MCP gateway (ADR-031)

### Infrastructure

- [Docker Compose](skills/infrastructure/docker-compose.md)
- [Caddy](skills/infrastructure/caddy.md)
- [Dragonfly](skills/infrastructure/dragonfly.md)

### Frontend

- [CopilotKit](skills/frontend/copilotkit.md) — HITL React UI
- [React](skills/frontend/react.md)

### NLP

- [Semantica](skills/nlp/semantica.md) — forensic NLP engine (py-mcp-server, authoritative)
- [FastMCP](skills/nlp/fastmcp.md)
- [DPK HAP](skills/nlp/dpk-hap.md)
- [DPK PII Redactor](skills/nlp/dpk-pii-redactor.md)
- [Voice Fingerprinting](skills/nlp/voice-fingerprinting.md)

### Database

- [PostgreSQL](skills/database/postgresql.md)
- [DuckDB](skills/database/duckdb.md)
- [LanceDB](skills/database/lancedb.md)
- [Neo4j](skills/database/neo4j.md)

### Security

- [Keycloak](skills/security/keycloak.md)

## Archived Entries (DIAL Stack)

Archived per ADR-033, 2026-04-21. Full content preserved at:

| Original | Archive Location | Reason |
|----------|-----------------|--------|
| `skills/infrastructure/ai-dial-core.md` | `archive/skills/infrastructure/ai-dial-core.md` | DIAL deprecated, never operational |
| `skills/infrastructure/AI_DIAL_EXPERT.md` | `archive/skills/infrastructure/AI_DIAL_EXPERT.md` | DIAL deprecated |
| `skills/frontend/dial-chat.md` | `archive/skills/frontend/dial-chat.md` | DIAL deprecated |
| `skills/dial-codebase-analysis/SKILL.md` | `archive/skills/dial-codebase-analysis/SKILL.md` | DIAL deprecated |
| `project-docs/components/infrastructure/ai-dial-core.md` | `archive/project-docs/components/infrastructure/ai-dial-core.md` | DIAL deprecated |
| `project-docs/components/infrastructure/AI_DIAL_EXPERT.md` | `archive/project-docs/components/infrastructure/AI_DIAL_EXPERT.md` | DIAL deprecated |
| `project-docs/components/frontend/dial-chat.md` | `archive/project-docs/components/frontend/dial-chat.md` | DIAL deprecated |

## Change Log

- 2026-04-21, rev 3, Computer: Added Conductor OSS section (ADR-033). Archived all DIAL stack entries. Fixed stale absolute path links from prior versions. Added Orchestration Contract and ADR register to quick nav.
- 2026-04-08, rev 2, Codex: Replaced broken skill-centric navigation with links to the actual live docs tree.
