# MCP Platform — Master Overview
> **Authoritative companion to GROUND_TRUTH.md.** This document is the narrative overview of the platform — what it is, how it works, and what phases it follows. GROUND_TRUTH.md wins any direct conflict with this document.
> Last updated: 2026-04-21 | Supersedes all prior versions of PLATFORM_OVERVIEW.md

---

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Every phase, every major task, and every architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Platform Vision

The MCP Platform is a forensic evidence processing system designed to ingest, analyze, and present digital communications evidence for active custody litigation (Salem v. Kinzel, No. 2025-53985-DC, Genesee County, Michigan 7th Judicial Circuit).

It supports multi-source ingestion — SMS, Facebook Messenger, iMessage, documents — applies structured NLP analysis pipelines, and presents evidence through a human-in-the-loop (HITL) review interface with full chain of custody.

**Core principles:**
1. **Forensic integrity** — SHA-256 at first touch, WORM for Pass 1, unbroken chain of custody
2. **Privacy-first** — Local processing required; cloud engines require explicit opt-in and owner approval per-engine
3. **Multi-source** — No single message format or document type is assumed
4. **Human oversight** — No analysis result is acted upon without human review at defined gates
5. **Audit trail** — Every operation is logged; every decision has a record
6. **Alpha 1 first** — Proven logic is ported from Alpha 1, never rewritten from scratch

---

## Current Architecture (ADR-033 — as of 2026-04-21)

### Platform Stack

| Component | Role | Port | Status |
|-----------|------|------|--------|
| **ContextForge** | MCP gateway — federates MCP servers, Keycloak auth edge, plugin pipeline (PII tagging, content moderation, secrets detection) | 4444 | NOT DEPLOYED |
| **Conductor OSS** | Orchestration + AI layer — replaces Agno + n8n (ADR-033). Deterministic workflows, HITL gates, LLM task execution, CALL_MCP_TOOL workers | TBD | NOT DEPLOYED — **CONDUCTOR GATE active** |
| **LiteLLM** | Model proxy — 14+ providers (OpenAI, Anthropic, Gemini, Ollama, Groq, etc.) unified API | TBD | NOT DEPLOYED |
| **Directus** | Admin/data surface — evidence browser, REST/GraphQL over PostgreSQL, RBAC for Matt | 8055 | NOT DEPLOYED — activation requires approval |
| **TS MCP Server** | Parsers, DuckDB vault, PostgreSQL writes, ReviewQueue (HITL approve/reject) | 8081 | PARTIALLY BUILT — 22 working tools, 2 stubs |
| **Py MCP Server** | Semantica NLP, LanceDB, Neo4j, document intelligence engine router | 8082 | PARTIALLY BUILT — 25 working tools, 11 stubs |
| **JS MCP Server** | Text utilities, format handlers | 8083 | PARTIALLY BUILT — ping only |
| **NLUX React (`@nlux/react`)** | Embedded `<AiChat />` case copilot | client/ | NOT DEPLOYED |
| **CopilotKit** | HITL evidence review UI | 3002/5173 | STUB ONLY |
| **OpenWebUI** | Remote chat interface routed through ContextForge | 3001 | NOT DEPLOYED — activation requires approval |
| **LibreChat** | Alternative remote chat with document upload, routed through ContextForge | 3003 | NOT DEPLOYED — activation requires approval |
| **Keycloak** | OIDC/JWT auth — gates all external access | 8180 | EXISTS IN DOCKER COMPOSE |
| **Caddy** | HTTPS termination, reverse proxy | 80/443 | EXISTS IN CONFIG |
| **WunderGraph Cosmo** | GraphQL federation across subgraphs | 4000 | EXISTS IN DOCKER COMPOSE |
| **PostgreSQL + pgvector** | Evidence store, app data, normalized analysis results | 5432 | EXISTS IN DOCKER COMPOSE |
| **DuckDB** | Fingerprint vault — SHA-256, UUIDv7, dedup, WORM (embedded, no network) | — | EXISTS |
| **LanceDB** | Vector embeddings (embedded, no network) | — | EXISTS |
| **Neo4j** | Knowledge graph — entities, relations, temporal facts | 7687 | EXISTS IN DOCKER COMPOSE — not populated |

**Nothing is running. Docker Compose exists but no containers have been started with owner approval.**

---

## Deprecated Components (Do Not Reference in Code)

| Component | Reason | Archive |
|-----------|--------|---------|
| AI DIAL Core | Replaced by ContextForge (ADR-031) + LiteLLM | `docs/wiki/archive/skills/infrastructure/ai-dial-core.md` |
| DIAL Chat | Replaced by NLUX React + OpenWebUI/LibreChat | `docs/wiki/archive/skills/frontend/dial-chat.md` |
| Agno | Replaced by Conductor OSS (ADR-033) | `_DEPRECATED/` |
| n8n | Replaced by Conductor OSS (ADR-033) | `_DEPRECATED/` |

---

## Access Surfaces (ADR-031)

Two distinct surfaces. **Internal API is the canonical interface. MCP tools are thin wrappers over it.**

### External (MCP Surface)
External tools connect via MCP protocol through ContextForge + Keycloak:
```
OpenWebUI / LibreChat / Claude Code / OpenCode
           ↓
      ContextForge (port 4444)
      Plugin pipeline: PII tagging → content moderation → secrets detection
           ↓ (Keycloak-gated)
      TS MCP Server (8081) | Py MCP Server (8082) | JS MCP Server (8083)
```

### Internal (Direct API Surface)
Internal components connect directly to internal APIs without the MCP hop:
```
Conductor workers / Directus → internal API → same tool implementations
```

### Chat Routing
```
OpenWebUI / LibreChat
      ↓
ContextForge → LiteLLM → [OpenAI / Anthropic / Ollama / Groq / ...]
                       → Conductor (workflow control)
                       → TS/Py/JS MCP servers (tool calls)
```

---

## ContextForge Role

ContextForge is the MCP gateway and plugin pipeline. It does not route AI model traffic (that is LiteLLM's job). Its specific responsibilities:

1. **MCP federation** — routes tool calls to the correct MCP server (TS/Py/JS)
2. **Auth gate** — Keycloak JWT validation before any tool call reaches the servers
3. **PII tagging** (permissive mode) — detects SSN, email, phone, credit cards; adds `contextforge_tags` to evidence records
4. **Content moderation** (permissive mode) — flags hate/violence/self-harm content for review
5. **Secrets detection** (permissive mode) — flags AWS keys, API keys, private key material in submitted content

Plugin output is metadata only — original files are never modified. Tags are stored in PostgreSQL `contextforge_tags` column for downstream use by Semantica and the review queue.

---

## Conductor OSS Role (ADR-033)

Conductor replaces both Agno (AI agent orchestration) and n8n (deterministic workflows) as the single orchestration layer.

**What it covers:**

| Former component | Conductor equivalent |
|-----------------|---------------------|
| n8n workflows | DAG workflow definitions — sequential, parallel, fork/join, switch, sub-workflow |
| n8n HITL gates | `HUMAN` task — native approval gate; fires signal to CopilotKit review UI |
| n8n webhooks | `WAIT` task (signal, duration, datetime) |
| Agno agent orchestration | `LLM_CHAT_COMPLETE`, `LLM_TEXT_COMPLETE` — multi-turn AI with tool calling |
| Agno dynamic tool calling | `CALL_MCP_TOOL` — calls any tool on TS/Py/JS servers from workflow steps |
| Agno RAG | `LLM_STORE_EMBEDDINGS`, `LLM_SEARCH_INDEX`, `LLM_GET_EMBEDDINGS` |

**CONDUCTOR GATE (hard stop):** Conductor integration does not begin until the first successful end-to-end ingest test passes. Gate condition: one evidence file fully ingested → hashed → stored → retrievable.

**OQ-C5 (unresolved):** When a Conductor `HUMAN` task fires, it must sync with `app.review_queue` and notify the CopilotKit UI. The bridge mechanism is not yet designed. Do not decide unilaterally.

---

## Ingestion Pipeline (Target State)

```
Raw Evidence File
      ↓
ContextForge (plugin tagging: PII, content moderation, secrets)
      ↓
TS MCP Server: EvidenceIngestor.ts
      ├── DuckDB (T1): SHA-256 fingerprint, UUIDv7, dedup check, WORM flag
      ├── PostgreSQL (T2): normalized record insert, contextforge_tags column populated
      └── parallel:
           ├── Py MCP Server: LanceDB (T2): embedding write
           └── Py MCP Server: Semantica → Neo4j (T3): NER, relations, temporal facts
                                                       (uses contextforge_tags for prioritization)
      ↓
Conductor HUMAN task (if flagged for review)
      ↓
CopilotKit UI: human reviewer approves/rejects
      ↓
ReviewQueue.ts: decision recorded with audit trail
```

**Storage tiers (never skip T1):**
- **T1 DuckDB** — SHA-256, UUIDv7, dedup, master clock (always first)
- **T2 PostgreSQL** — normalized evidence, app data, contextforge_tags
- **T2 LanceDB** — vector embeddings
- **T3 Neo4j** — knowledge graph (Semantica)

---

## Alpha 1 Reference (Read-Only — Never Modify)

Alpha 1 repo: `https://github.com/Cursedpotential/mcp-tool-platform`
Local path: `C:\Users\matts\Projects\TheBigOne\MCP_Tool_Platform\`

Before writing any new implementation, search Alpha 1 first.

| Alpha 1 Asset | Location | Alpha 2 Action |
|--------------|----------|----------------|
| Messaging schemas | `server/mcp/loaders/production-message-schemas.ts` | PORT + MERGE (add Alpha 2 fields, never replace Alpha 1 fields) |
| Facebook parser | `server/mcp/loaders/` | PORT to `FacebookExportParser.ts` — **port priority #1** |
| iMessage parser | `server/mcp/loaders/` | PORT to `ImessagePdfParser.ts` — **port priority #2** |
| Pattern analyzer | `server/mcp/analysis/` | PORT to py-mcp-server |
| Chain of custody | `server/mcp/custody/` | PORT to ts-mcp-server |
| Evidence hasher | `server/mcp/hasher/` | PORT to ts-mcp-server |
| HurtLex NLP | `server/mcp/nlp/` | PORT to py-mcp-server |
| Review queue | `server/mcp/review/` | ALREADY PORTED — verify parity |
| Schema migration | `server/mcp/loaders/production-message-schemas.ts` | PORT priority #3 |

> Verify actual file paths by reading Alpha 1 directly. This table is a guide.

---

## Document Intelligence Architecture

The document intelligence router is a pluggable component in the Py MCP Server. All engines sit behind a common `EngineRouter` interface.

```
ingest_evidence (MCP Tool)
        ↓
  EngineRouter
  ├── Pandoc      [local]  stub → port priority after parsers
  ├── Tesseract   [local]  stub → port priority after parsers
  ├── DocTR       [local]  stub only
  ├── Docling     [local]  stub only
  ├── OCRopus     [local]  stub only
  ├── Unstructured [local/API] stub only
  ├── GLM-OCR     [local]  planned
  ├── LlamaParse  [cloud]  DEFERRED — requires owner approval
  ├── Google DocAI [cloud] DEFERRED — requires owner approval
  ├── AWS Textract [cloud] DEFERRED — requires owner approval
  └── IBM watsonx [cloud]  DEFERRED — requires owner approval
```

Routing priority: local engines first (zero cost, no data egress). Cloud engines only when (a) local engines cannot process the document AND (b) owner has explicitly approved that engine by name.

---

## Current State (2026-04-21)

| Layer | Component | Status |
|-------|-----------|--------|
| MCP gateway | ContextForge | NOT DEPLOYED |
| Orchestration | Conductor OSS | NOT DEPLOYED — CONDUCTOR GATE active |
| Model proxy | LiteLLM | NOT DEPLOYED |
| Auth | Keycloak | IN DOCKER COMPOSE — not started |
| Routing | Caddy | IN CONFIG — not started |
| GraphQL federation | WunderGraph Cosmo | IN DOCKER COMPOSE — not started |
| Admin surface | Directus | IN DOCKER COMPOSE — activation requires approval |
| Tool execution | TS MCP Server | PARTIALLY BUILT — 22 working, 2 stubs |
| Tool execution | Py MCP Server | PARTIALLY BUILT — 25 working, 11 stubs (doc intel engines) |
| Tool execution | JS MCP Server | PARTIALLY BUILT — ping only |
| Parsing | SMS XML | WORKING |
| Parsing | Facebook JSON | STUB — port priority #1 |
| Parsing | iMessage | STUB — port priority #2 |
| NLP | Semantica | PARTIALLY BUILT — do not rewrite |
| Storage | DuckDB (T1) | EXISTS |
| Storage | PostgreSQL (T2) | IN DOCKER COMPOSE |
| Storage | LanceDB (T2) | EXISTS |
| Storage | Neo4j (T3) | IN DOCKER COMPOSE — not populated |
| UI | CopilotKit React | STUB ONLY |
| UI | NLUX React | NOT DEPLOYED |
| UI | OpenWebUI | NOT DEPLOYED |
| UI | LibreChat | NOT DEPLOYED |

---

## Phase Roadmap

All phases require explicit owner approval gate before the next phase begins. "Approved in principle" is not approval. The phrase is: **"approved — proceed [exact task name]"**.

---

### Phase 0 — Foundation Audit (prerequisite for all phases)

**Objective**: Establish a verified baseline before any new implementation.

| Task | Description |
|------|-------------|
| 0-01 | Audit Alpha 1 — catalog all reusable assets, verify file paths from table above |
| 0-02 | Verify storage tiers are healthy (DuckDB, PostgreSQL, LanceDB, Neo4j) |
| 0-03 | Verify MCP servers respond on health checks (8081, 8082, 8083) |
| 0-04 | Verify Keycloak auth (8180) and Caddy routing |
| 0-05 | Run existing test suites — establish baseline pass/fail counts |
| 0-06 | Confirm `production-message-schemas.ts` is present and readable in Alpha 1 |
| 0-07 | Confirm DuckDB vault SHA-256 fingerprinting works end-to-end |

**Phase 0 outputs**: Alpha 1 inventory, health check report, baseline test results.

> 🛑 **Owner approval required before Phase 1 begins.**

---

### Phase 1 — Core Ingestion (most urgent)

**Objective**: Files go in → SHA-256 hash at first touch → chain of custody established → messages normalized and stored. This is **Outcome 1** from GROUND_TRUTH.md.

#### 1.1 Messaging Schema Port

| Task | Description |
|------|-------------|
| 1.1-01 | Read and document all field definitions in Alpha 1 `production-message-schemas.ts` |
| 1.1-02 | Port SMS schema: Alpha 1 fields + Alpha 2 extensions (pgvector, device_id, WAL) |
| 1.1-03 | Port Facebook schema: Alpha 1 fields + Alpha 2 extensions |
| 1.1-04 | Port iMessage schema: Alpha 1 fields + Alpha 2 extensions |
| 1.1-05 | Write migration scripts for PostgreSQL schema changes (migrations/00N_description.sql) |
| 1.1-06 | Validate SMS parser still passes all existing tests after schema changes |

#### 1.2 Facebook and iMessage Parsers (Stub → Working)

| Task | Description |
|------|-------------|
| 1.2-01 | Read Alpha 1 Facebook parser — document field coverage before writing any code |
| 1.2-02 | Implement Facebook JSON parser — full field extraction |
| 1.2-03 | Map Facebook output to normalized `EvidenceBatch` |
| 1.2-04 | Read Alpha 1 iMessage parser — document field coverage before writing any code |
| 1.2-05 | Implement iMessage SQLite/plist parser — full field extraction |
| 1.2-06 | Map iMessage output to normalized `EvidenceBatch` |
| 1.2-07 | Integration tests for both parsers against Alpha 1 fixture data |

#### 1.3 DuckDB → PostgreSQL Pipeline Verification

| Task | Description |
|------|-------------|
| 1.3-01 | Verify DuckDB → PostgreSQL end-to-end with SMS evidence (existing working path) |
| 1.3-02 | Wire Facebook and iMessage parsers through the same pipeline |
| 1.3-03 | Verify chain of custody record is written for every ingestion |

#### 1.4 ContextForge — Initial Deployment

| Task | Description |
|------|-------------|
| 1.4-01 | Add ContextForge service to `docker-compose.yml` |
| 1.4-02 | Configure PII filter, content moderation, secrets detection in permissive (tagging) mode |
| 1.4-03 | Register TS/Py/JS MCP servers with ContextForge |
| 1.4-04 | Configure Keycloak client for ContextForge |
| 1.4-05 | Smoke test: tool call via ContextForge reaches TS MCP Server and returns result |
| 1.4-06 | Verify `contextforge_tags` column populated in evidence table after tagging |

#### 1.5 Directus Activation

| Task | Description |
|------|-------------|
| 1.5-01 | Review Directus docker-compose service definition for correctness |
| 1.5-02 | Start Directus container, verify health |
| 1.5-03 | Configure Directus PostgreSQL connection (read-only for evidence tables) |
| 1.5-04 | Configure RBAC (admin role, reviewer role) |
| 1.5-05 | Register Directus as Keycloak OIDC client |
| 1.5-06 | Expose Directus via Caddy at `/admin` |
| 1.5-07 | Smoke test: evidence tables browsable in Directus UI |

**Phase 1 outputs**: Facebook + iMessage parsers working, ContextForge deployed with tagging pipeline, Directus operational, first end-to-end ingest test passes. **CONDUCTOR GATE lifts when this passes.**

> 🛑 **Owner approval required before Phase 2 begins.**

---

### Phase 2 — Search (Outcome 2)

**Objective**: Ingested evidence is searchable semantically and by keyword.

**Prerequisite**: Phase 1 complete. CONDUCTOR GATE lifted.

| Task | Description |
|------|-------------|
| 2-01 | Confirm sentence-transformers model selection with owner |
| 2-02 | Implement `EmbeddingService` in py-mcp-server |
| 2-03 | Wire embedding pipeline to post-parse ingestion path |
| 2-04 | LanceDB batch upsert write path |
| 2-05 | pgvector fallback write path |
| 2-06 | Register `evidence_search` MCP tool (semantic + keyword) |
| 2-07 | Neo4j population from Semantica NER pipeline |
| 2-08 | OpenWebUI integration (if approved) — routes through ContextForge |
| 2-09 | LibreChat integration (if approved) — routes through ContextForge |
| 2-10 | LiteLLM deployment — unified model proxy for all LLM calls |

#### 2.1 Conductor — Initial Deployment (post-GATE)

| Task | Description |
|------|-------------|
| 2.1-01 | Add Conductor server + Redis to docker-compose.yml |
| 2.1-02 | Confirm Conductor backend: Postgres (preferred, ADR-033 OQ-C3) vs Elasticsearch |
| 2.1-03 | Design first workflow: evidence ingest DAG (DuckDB → PostgreSQL → LanceDB + Neo4j) |
| 2.1-04 | Implement CALL_MCP_TOOL worker pointing to TS MCP Server evidence tools |
| 2.1-05 | Design OQ-C5 bridge: HUMAN task ↔ ReviewQueue.ts ↔ CopilotKit notification |
| 2.1-06 | First end-to-end workflow run — single file through Conductor-orchestrated ingest |

**Phase 2 outputs**: `evidence_search` working, Conductor deployed, first Conductor workflow running, Neo4j populated, OpenWebUI/LibreChat operational (if approved).

> 🛑 **Owner approval required before Phase 3 begins.**

---

### Phase 3 — Analysis and Output (Outcome 3)

**Objective**: Evidence generates court-ready documents, timelines, and reports.

**Prerequisite**: Phase 2 complete.

| Task | Description |
|------|-------------|
| 3-01 | Port pattern analyzer from Alpha 1 `server/mcp/analysis/` to py-mcp-server |
| 3-02 | Port HurtLex NLP from Alpha 1 `server/mcp/nlp/` to py-mcp-server |
| 3-03 | Port chain of custody from Alpha 1 `server/mcp/custody/` to ts-mcp-server |
| 3-04 | Implement Pass 1 full analysis pipeline (24-hour window partitioning, WORM enforcement) |
| 3-05 | Register `run_pass1_analysis` MCP tool |
| 3-06 | Local document intelligence engines: Pandoc + Tesseract (stub → working) |
| 3-07 | Document intelligence fallback chain: Pandoc → Tesseract → error |
| 3-08 | Timeline generator — port from Alpha 1 if exists, otherwise new |
| 3-09 | Court document export format — design with owner before implementing |

#### 3.1 Local Document Intelligence Expansion

| Task | Description |
|------|-------------|
| 3.1-01 | Implement DocTR neural OCR engine (approval required) |
| 3.1-02 | Implement Docling document understanding engine (approval required) |
| 3.1-03 | Implement OCRopus historical document engine (approval required) |
| 3.1-04 | Implement Unstructured.io engine local mode (approval required) |

#### 3.2 Cloud Engine Integration (conditional — each requires individual approval)

| Engine | Activation condition |
|--------|---------------------|
| LlamaParse | Local engines cannot process document type + owner approval naming this engine |
| Google DocAI | Same |
| AWS Textract | Same |
| IBM watsonx | Same |

**Phase 3 outputs**: Pass 1 analysis complete, document intelligence engines operational, timeline generation working.

> 🛑 **Owner approval required before Phase 4 begins.**

---

### Phase 4 — HITL Review + CopilotKit

**Prerequisite**: Phase 3 complete.

| Task | Description |
|------|-------------|
| 4-01 | Complete CopilotKit integration with evidence review workflow |
| 4-02 | NLUX React `<AiChat />` embedded copilot wired to LiteLLM + Conductor |
| 4-03 | OQ-C5 bridge: Conductor HUMAN task ↔ ReviewQueue.ts ↔ UI notification |
| 4-04 | Approval audit trail: every HITL decision recorded with timestamp and reviewer ID |
| 4-05 | Multi-reviewer support (requires separate owner approval) |

> 🛑 **Owner approval required before Phase 5 begins.**

---

### Phase 5 — Production Hardening

| Task | Description |
|------|-------------|
| 5-01 | Performance testing — establish throughput baselines |
| 5-02 | Security review — all external surfaces Keycloak-gated, no leaked credentials |
| 5-03 | Backup and recovery procedures |
| 5-04 | Operational runbooks |
| 5-05 | Evidence export for court use — format and process defined with owner |

> 🛑 **Owner approval required before any production deployment.**

---

## Architectural Decision Summary (Current)

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-002 | MCP Protocol for tool execution | Accepted |
| ADR-003 | Three-server MCP architecture (TS/Py/JS) | Accepted |
| ADR-004 | DuckDB as fingerprint vault (T1) | Accepted |
| ADR-005 | PostgreSQL as evidence store | Accepted |
| ADR-006 | LanceDB for vector embeddings | Accepted |
| ADR-007 | Neo4j for knowledge graph | Accepted |
| ADR-008 | Keycloak for OIDC/JWT | Accepted |
| ADR-009 | Caddy for HTTPS/routing | Accepted |
| ADR-010 | WunderGraph Cosmo for GraphQL federation | Accepted |
| ADR-011 | SHA-256 at first touch | Accepted |
| ADR-012 | WORM for Pass 1 records | Accepted |
| ADR-013 | Alpha 1 as read-only reference | Accepted |
| ADR-015 | UUIDv7 primary keys | Accepted |
| ADR-016 | EvidenceBatch as normalized output contract | Accepted |
| ADR-017 | Coordinator pattern for evidence operations | Accepted |
| ADR-019 | W3C PROV-O for provenance chains | Accepted |
| ADR-020 | Docker Compose for local development | Accepted |
| ADR-021 | Directus as admin/data surface | Accepted — activation requires approval |
| ADR-022 | SurrealDB deferred | Deferred |
| ADR-023 | Multi-engine document intelligence (pluggable router) | Accepted — each engine requires approval |
| ADR-024 | Document intelligence engines are opt-in | Accepted |
| ADR-025 | Messaging schemas — port from Alpha 1 + Alpha 2 extensions | Accepted — port requires approval |
| ADR-026 | UI: CopilotKit + OpenWebUI + LibreChat | Proposed — all require approval; routing through ContextForge (not DIAL Core) |
| ADR-027 | Open Structured Memory as canonical memory system | Accepted |
| ADR-028 | Hierarchical memory architecture | Accepted |
| ADR-029 | GROUND_TRUTH.md as mandatory first read | Accepted |
| ADR-030 | Platform components are peers — no hierarchy | Accepted |
| ADR-031 | Two access surfaces — MCP external and internal API direct | Accepted |
| ADR-033 | Conductor OSS replaces Agno + n8n | Accepted |
| ADR-001 | ~~DIAL Core as AI gateway~~ | **Superseded by ADR-031 (ContextForge) + LiteLLM** |

---

## Hard Rules for All Agents

1. **Alpha 1 first.** Before writing any code, check `MCP_Tool_Platform/` for an existing implementation. Port it; do not rewrite it.
2. **Do not touch working code** unless fixing a direct bug caused by your changes.
3. **No stubs.** No `TODO:`, `FIXME:`, `throw new Error("not implemented")`, `pass # stub`. Implement fully or defer with explicit owner approval.
4. **No deletions.** Move to `_DEPRECATED/` instead.
5. **No container starts** without Matt saying "approved — proceed [service name]".
6. **No cloud API wiring** without explicit owner approval naming the engine.
7. **No schema changes** without a numbered migration file.
8. **No hardcoded secrets.** Everything in `.env`.
9. **CONDUCTOR GATE.** No workflow definitions committed without `// GATE-LIFTED: <date> <approver>` marker. Gate lifts only after first end-to-end ingest test passes.
10. **Semantica is VIP.** Do not rewrite its interfaces. Extend through its defined API. Flag any Semantica tool that is missing or broken — do not work around it.
11. **ContextForge gates all external access.** No MCP tool call reaches the servers without going through ContextForge + Keycloak.
12. **Internal API is canonical.** Business logic lives in internal API handlers. MCP tools are thin wrappers.
13. **Memory write-back is mandatory.** Cascade deepest → root at every session end.
14. **Approval language.** Only `approved — proceed` is approval. "looks good", "yes", silence are not approval.

---

## Open Architectural Questions (Do Not Resolve Without Owner)

| # | Question | Blocking |
|---|----------|---------|
| OQ-1 | OpenCode: server mode vs agent mode | OpenCode integration |
| OQ-2 | Internal API design: REST vs GraphQL vs gRPC | Conductor worker ↔ tool server integration |
| OQ-5 | Embedding model: which sentence-transformers model | Embedding pipeline |
| OQ-C3 | Conductor backend: Elasticsearch vs Postgres | Conductor deployment |
| OQ-C5 | HUMAN task ↔ ReviewQueue.ts ↔ CopilotKit notification bridge | HITL gate implementation |

---

*Full decision register: `DECISION_REGISTER.md`*
*Authoritative state: `GROUND_TRUTH.md`*
*Session behavior: `MCP_PLATFORM_SYSTEM_PROMPT_V3.md`*
*Agent governance: `ORCHESTRATION_CONTRACT.md`*
