---
title: Conductor OSS — Platform Overview
type: reference
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - orchestration
  - adr-033
  - architecture
adr: ADR-033
---

# Conductor OSS — Platform Overview

## What It Is

Conductor OSS is an open-source durable execution and workflow orchestration engine. It manages long-running, stateful workflows across distributed workers with at-least-once delivery, saga-pattern compensation, and native AI/LLM task types.

- **License**: Apache 2.0
- **Source**: https://github.com/conductor-oss/conductor
- **Docs**: https://conductor-oss.github.io/conductor/
- **Orkes Cloud**: https://orkes.io

## Role in MCP_PLATFORM

Conductor is the **single orchestration layer**. It replaced two components per ADR-033:

| Replaced | With | Reason |
|----------|------|--------|
| **Agno** (agent runtime) | Conductor workflow engine | Native DO_WHILE, LLM_CHAT_COMPLETE, HUMAN task types cover all agent patterns |
| **n8n** (low-code automation) | Conductor workflows | Conductor handles all automation needs with stronger guarantees and AI-native primitives |

ContextForge (ADR-031) remains the MCP gateway — it is **not** replaced by Conductor. Conductor orchestrates workflows that call MCP tools through ContextForge.

## Architecture Position

```
User / CopilotKit HITL UI
         │
         ▼
  ContextForge (MCP gateway, ADR-031)
         │
         ▼
  Conductor OSS (orchestration engine)
    ├── LLM_CHAT_COMPLETE tasks → LiteLLM → 14+ LLM providers
    ├── CALL_MCP_TOOL tasks → ts-mcp-server / py-mcp-server / js-mcp-server
    ├── HUMAN tasks → app.review_queue (PostgreSQL) ← OPEN QUESTION OQ-C5
    ├── DO_WHILE loops (agent iteration)
    ├── FORK_JOIN_DYNAMIC (parallel ingestion)
    └── SWITCH (conditional routing)
         │
         ▼
  MCP Workers (ts-mcp-server · py-mcp-server · js-mcp-server)
    └── Semantica (forensic NLP, py-mcp-server — authoritative, do not rewrite)
```

## ADR-033 Summary

**Decision**: Replace Agno and n8n with Conductor OSS as the single orchestration and AI agent execution layer.

**Rationale**:
- Conductor OSS includes all AI task types confirmed present in the open-source release (not enterprise-only)
- `LLM_CHAT_COMPLETE`, `DO_WHILE`, `FORK_JOIN_DYNAMIC`, `HUMAN`, `LIST_MCP_TOOLS`, `CALL_MCP_TOOL` are all in OSS
- Supports 14+ LLM providers natively
- Single technology reduces operational surface area
- Durable execution: survives restarts, worker crashes, network failures
- Full execution history preserved indefinitely for forensic audit trail
- JSON workflow definitions are LLM-generatable and versionable

**Status**: Decision final. Agno and n8n removed from platform.

## CONDUCTOR GATE

> **No Conductor integration is merged into main until the first end-to-end ingest test passes.**

This gate exists because:
- Nothing is running yet — no containers started
- TS server has 2 stubs (facebook, imessage parsers — priority ports #1 and #2)
- Py server has 11 stubs (doc intel engines — Pandoc + Tesseract first)
- HUMAN task → `app.review_queue` bridge is an open question (OQ-C5)

The gate lifts when: a single message ingested via ContextForge completes a full Conductor workflow execution through at least one MCP worker and produces a verifiable output in PostgreSQL.

## Open Questions (Conductor)

| ID | Question | Status |
|----|----------|--------|
| OQ-C1 | Which persistence backend for Conductor in prod? (Redis+Postgres vs Elasticsearch) | Open |
| OQ-C2 | Worker deployment pattern — sidecar containers vs standalone worker pods? | Open |
| OQ-C3 | Conductor server auth for prod deployment (Orkes RBAC vs OSS API key)? | Open |
| OQ-C4 | Workflow versioning strategy — when to bump vs in-place update? | Open |
| OQ-C5 | HUMAN task → `app.review_queue` bridge design — poll vs webhook vs direct PostgreSQL worker? | Open |

## Related

- [OSS_REFERENCE.md](OSS_REFERENCE.md) — engine capabilities
- [PLATFORM_IMPLEMENTATION.md](PLATFORM_IMPLEMENTATION.md) — how we implement it
- [ECOSYSTEM.md](ECOSYSTEM.md) — tools, plugins, MCP server
- ADR-033 in `DECISION_REGISTER_POST_DIAL.md`
