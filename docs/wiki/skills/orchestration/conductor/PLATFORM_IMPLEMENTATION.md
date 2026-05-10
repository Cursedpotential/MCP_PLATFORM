---
title: Conductor — MCP_PLATFORM Implementation
type: reference
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - implementation
  - mcp-platform
  - workers
  - human-task
  - review-queue
adr: ADR-033
gate: CONDUCTOR_GATE
---

# Conductor — MCP_PLATFORM Implementation

How MCP_PLATFORM uses Conductor. This is the implementation plan — **nothing is running yet**. The CONDUCTOR GATE blocks any merge until first end-to-end ingest test passes.

## Current State

- Conductor OSS: **not deployed**
- Workers: **not registered**
- Workflows: **not defined**
- Gate status: **LOCKED** (no end-to-end ingest test has passed)

Port priority before Conductor integration begins:
1. facebook-parser (TS server stub)
2. imessage-parser (TS server stub)
3. schema migration
4. chain-custody
5. hurtlex
6. pattern-analyzer
7. timeline-generator

## Planned Architecture

### Worker → MCP Server Mapping

Each MCP server registers workers that poll Conductor for tasks:

| Worker Task Type | MCP Server | Language | Status |
|------------------|-----------|----------|--------|
| `ts.parse.*` | ts-mcp-server | TypeScript | Planned |
| `ts.db.*` | ts-mcp-server | TypeScript | Planned |
| `py.nlp.*` | py-mcp-server (Semantica) | Python | Planned |
| `py.graph.*` | py-mcp-server | Python | Planned |
| `py.vector.*` | py-mcp-server | Python | Planned |
| `js.legacy.*` | js-mcp-server | JavaScript | Planned |

Workers run inside MCP server containers — they poll outbound to the Conductor server. No inbound firewall rules required.

### Core Workflow Patterns

#### Evidence Ingest Workflow

```
ingest_trigger
  └── FORK_JOIN_DYNAMIC (fan out per parser type)
        ├── ts.parse.facebook
        ├── ts.parse.imessage
        ├── ts.parse.sms
        └── ts.parse.whatsapp
  └── JOIN
  └── py.nlp.semantica_extract
  └── py.graph.build_knowledge_graph
  └── HUMAN (review gate → app.review_queue)
  └── py.vector.index_embeddings
  └── ts.db.write_postgresql
```

#### Agent Reasoning Loop (DO_WHILE)

```
DO_WHILE (max_iterations: configurable)
  └── LLM_CHAT_COMPLETE (via LiteLLM → model provider)
  └── SWITCH on action
        ├── "TOOL" → CALL_MCP_TOOL → SET_VARIABLE
        └── "FINAL" → TERMINATE with answer
```

#### Human Review Gate

```
... upstream tasks ...
└── HUMAN (taskReferenceName: "review_gate")
      └── Blocks until app.review_queue entry updated
└── SWITCH on review decision
      ├── "approved" → continue pipeline
      └── "rejected" → compensation workflow
```

### HUMAN Task → review_queue Bridge (OQ-C5)

**Open Question**: The Conductor `HUMAN` task pauses execution until externally signaled. The platform's existing review queue lives in `app.review_queue` (PostgreSQL). Bridging these requires one of:

**Option A — Poll Worker**: A dedicated TypeScript worker polls `app.review_queue` for status changes and signals the HUMAN task via Conductor's task signal API.

**Option B — Webhook**: CopilotKit/reviewer submits a decision that hits a Conductor webhook (Orkes only) or a thin Express endpoint that calls the signal API.

**Option C — Direct PostgreSQL Worker**: Conductor worker writes to `app.review_queue` when HUMAN task starts; reviewer updates row; trigger or cron worker signals Conductor when row resolves.

**Status**: OQ-C5 unresolved. Design decision required before HUMAN tasks can be implemented. `ReviewQueue.ts` exists and works — bridge design is the gap.

## Infrastructure Deployment

### Local (Docker Compose)

Add to `docker-compose.yml`:

```yaml
conductor-server:
  image: conductoross/conductor:latest
  ports:
    - "8080:8080"
  environment:
    - CONDUCTOR_DB=postgres
    - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/conductor
    - SPRING_DATASOURCE_USERNAME=${POSTGRES_USER}
    - SPRING_DATASOURCE_PASSWORD=${POSTGRES_PASSWORD}
  depends_on:
    - postgres
    - redis
```

**Note**: Conductor server runs on port 8080. DIAL Core was also on 8080 — DIAL is deprecated, port is available.

### Environment Variables (Workers)

```bash
CONDUCTOR_SERVER_URL=http://conductor-server:8080/api
# Auth only required if server has auth enabled
CONDUCTOR_AUTH_KEY=<key>
CONDUCTOR_AUTH_SECRET=<secret>
```

## Workflow Definition Conventions

1. All workflow names: `snake_case`
2. All task reference names: `snake_case` with descriptive suffix (`_task`, `_gate`, `_loop`)
3. `schemaVersion: 2` on all definitions
4. `failureWorkflow` defined for all production workflows
5. `restartable: true` on all workflows
6. Input/output schema documented in the workflow `description` field
7. Worker task types namespaced: `{server}.{domain}.{action}` (e.g., `ts.parse.facebook`)

## Integration with ContextForge

ContextForge (MCP gateway, ADR-031) is the inbound request boundary. Conductor is downstream of ContextForge:

1. ContextForge receives `/api/chat` request
2. ContextForge authenticates, routes, and selects workflow
3. ContextForge triggers Conductor workflow via REST API (`POST /api/workflow`)
4. Conductor orchestrates MCP workers
5. Results flow back through ContextForge to the client

ContextForge does **not** poll workers directly — Conductor owns that relationship.

## Integration with LiteLLM

All LLM calls from Conductor workflows route through LiteLLM:

```json
{
  "type": "LLM_CHAT_COMPLETE",
  "name": "reason_step",
  "inputParameters": {
    "llmProvider": "litellm",
    "model": "${workflow.input.model}",
    "messages": [...]
  }
}
```

LiteLLM abstracts provider selection — same workflow definition works with any of the 14+ supported providers.

## Semantica Integration Rule

Semantica is authoritative for forensic NLP. It runs as a py-mcp-server. Conductor calls it via `CALL_MCP_TOOL`:

```json
{
  "type": "CALL_MCP_TOOL",
  "name": "semantica_extract",
  "inputParameters": {
    "server": "py-mcp-server",
    "tool": "semantica_extract_entities",
    "input": "${parse_task.output.text}"
  }
}
```

**Rule**: Do not rewrite Semantica logic in Conductor tasks. Conductor calls Semantica; it does not replace it.

## Relevant Files

- `DECISION_REGISTER.md` — ADR-033
- `GROUND_TRUTH.md` — Conductor section
- `MCP_PLATFORM_SYSTEM_PROMPT_V3.md` — Section 2.1 architecture diagram, Section 3.5 CoT
- `ORCHESTRATION_CONTRACT.md` — agent governance, change gates
- `ReviewQueue.ts` — existing review queue implementation
