# Post-DIAL Master Overview — MCP Platform

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Platform Vision

The MCP Platform is a forensic evidence processing system designed to ingest, analyze, and present digital communications evidence. It supports multi-source ingestion (SMS, Facebook Messenger, iMessage, documents, and extensible to other formats), applies structured NLP analysis pipelines, and presents evidence through a HITL (human-in-the-loop) review interface with full chain of custody.

**Core principles**:
1. **Forensic integrity** — SHA-256 at first touch, WORM for Pass 1, unbroken chain of custody
2. **Privacy-first** — Local processing preferred; cloud engines require explicit opt-in and owner approval
3. **Multi-source** — No single message format or document type is assumed
4. **Human oversight** — No analysis result is acted upon without human review at defined gates
5. **Audit trail** — Every operation is logged; every decision has a record

---

## Strategic Direction

### DIAL Core as API Gateway
DIAL Core (port 8080) is the single entry point for all AI model interactions. It provides:
- Model routing and load balancing
- MCP tool dispatch to the three specialized servers
- Authentication integration with Keycloak
- Observability (request/response logging)

All agents and client applications communicate with DIAL Core. No agent makes direct model API calls.

### MCP Servers as Tool Executors
Three specialized MCP servers handle tool execution:
- **TS MCP Server** (port 8081): Document parsers, DuckDB/PostgreSQL storage writes, format detection
- **Py MCP Server** (port 8082): Semantica NLP pipeline, LanceDB vector operations, Neo4j graph writes
- **JS MCP Server** (port 8083): Text utilities, format handlers, lightweight transformations

### Directus as User-Facing Data/Admin Surface
Directus connects to PostgreSQL and provides:
- No-code data browser for evidence tables
- Auto-generated REST and GraphQL APIs
- Role-based access control (admin vs. reviewer roles)
- Export and reporting capabilities

**Status**: Added to docker-compose; requires owner approval before activation.

### CopilotKit + OpenWebUI + LibreChat as Chat Interfaces
- **CopilotKit** (embedded in `client/`): HITL evidence review interface tightly coupled to the review workflow
- **OpenWebUI**: Remote, general-purpose chat interface federating with DIAL Core — for operators who prefer a standalone UI
- **LibreChat**: Alternative remote chat interface with document upload support

All three route through DIAL Core. All require Keycloak gating before any external exposure.

### Document Intelligence Multi-Engine Router
Rather than committing to a single document processing engine, the platform uses a pluggable `EngineRouter` that:
- Selects the best available engine for each document type
- Prefers local engines (Pandoc, Tesseract, DocTR, Docling) for cost and privacy
- Falls back to cloud engines (Google DocAI, AWS Textract, LlamaParse) only when local engines cannot handle the document and the owner has approved cloud activation
- All engine activations are opt-in

See `docs/architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md` for the full engine matrix and routing logic.

### Alpha 1 Code as Reference
The Alpha 1 codebase in `MCP_Tool_Platform/` is the authoritative reference for proven logic. Before building any new component:
1. Check if Alpha 1 has a working implementation
2. If yes, port it — do not rewrite
3. Alpha 1 files are **never modified**
4. Alpha 1 messaging schemas (`production-message-schemas.ts`) are the starting point for all parser work

---

## Current State Summary

| Layer | Component | Status |
|-------|-----------|--------|
| Gateway | DIAL Core | ✅ Operational |
| Tool execution | TS MCP Server | ✅ Operational |
| Tool execution | Py MCP Server | ✅ Operational |
| Tool execution | JS MCP Server | ✅ Operational |
| Auth | Keycloak | ✅ Operational |
| Routing | Caddy | ✅ Operational |
| GraphQL federation | WunderGraph Cosmo | ✅ Operational |
| Storage — fingerprint vault | DuckDB | ✅ Operational |
| Storage — evidence | PostgreSQL + pgvector | ✅ Operational |
| Storage — vectors | LanceDB | ✅ Operational |
| Storage — graph | Neo4j | ⚠️ Configured, not populated |
| NLP | Semantica (NER, embeddings) | ✅ Operational |
| Parsing | SMS XML | ✅ Working |
| Parsing | Facebook JSON | ⚠️ Stub only |
| Parsing | iMessage | ⚠️ Stub only |
| Doc intelligence | Pandoc, Tesseract | ⚠️ Stub, needs approval |
| Doc intelligence | Cloud engines | ❌ Deferred |
| UI — HITL chat | CopilotKit React | ⚠️ Stub wired |
| UI — data surface | Directus | ⚠️ Added to compose, needs approval |
| UI — remote chat | OpenWebUI | 🔜 Planned |
| UI — remote chat | LibreChat | 🔜 Planned |
| Analysis | Pass 1 pipeline | 🔜 Not started |
| Analysis | Pass 2 pipeline | 🔜 Not started |

---

## Phase Roadmap

### Phase 0: Foundation Audit
- Audit Alpha 1 assets
- Confirm all storage tiers are healthy
- Establish baseline test coverage
- **STOP — owner approval required before Phase 1**

### Phase 1: Core Ingestion + Directus + Document Intelligence Foundation
- Activate Directus (with approval)
- Port messaging schemas from Alpha 1
- Implement Facebook and iMessage parsers
- Local document intelligence engines (Pandoc, Tesseract)
- Wire embedding pipeline
- Register `ingest_evidence`, `evidence_search` MCP tools
- **STOP — owner approval required before Phase 2**

### Phase 2: Engine Expansion + Cloud Provider Integration
- Cloud engine activation (if approved): Google DocAI, AWS Textract, LlamaParse
- Full embedding pipeline optimization
- OpenWebUI + LibreChat integration (if approved)
- Neo4j population from NER pipeline
- **STOP — owner approval required before Phase 3**

### Phase 3: Pass 1 Full Analysis Pipeline
- Port sentiment, intent, HurtLex from Alpha 1
- Implement 24-hour window partitioning
- WORM enforcement
- Register `run_pass1_analysis` MCP tool
- **STOP — owner approval required before Phase 4**

### Phase 4: HITL Review UI + CopilotKit Integration
- Complete CopilotKit integration
- Evidence review workflow
- Approval audit trail integration
- Multi-reviewer support (if approved)
- **STOP — owner approval required before Phase 5**

### Phase 5: Production Hardening
- Performance testing
- Security review
- Backup and recovery procedures
- Operational runbooks
- **STOP — owner approval required before any production deployment**

---

## Key Architectural Decisions Summary

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | DIAL Core as primary AI gateway | Accepted |
| ADR-004 | DuckDB as fingerprint vault | Accepted |
| ADR-011 | SHA-256 at first touch | Accepted |
| ADR-012 | WORM for Pass 1 records | Accepted |
| ADR-013 | Alpha 1 as read-only reference | Accepted |
| ADR-021 | Directus as data/admin surface | Accepted (activation pending approval) |
| ADR-022 | SurrealDB deferred | Deferred |
| ADR-023 | Multi-engine document intelligence | Accepted (engines pending approval) |
| ADR-024 | Engines are opt-in | Accepted |
| ADR-025 | Messaging schemas from Alpha 1 + Alpha 2 extensions | Accepted (port pending approval) |
| ADR-026 | CopilotKit + OpenWebUI + LibreChat | Proposed (all pending approval) |

Full decision register: `DECISION_REGISTER_POST_DIAL.md`

---

## Hard Rules for All Agents

1. **Alpha 1 first**: Before writing any code, check `MCP_Tool_Platform/` for an existing implementation. Port it; do not rewrite it.

2. **Never modify existing working code**: If a component is working, do not touch it unless fixing a direct bug caused by your changes.

3. **Messaging schema port discipline**: All messaging parser schema work starts from Alpha 1 `production-message-schemas.ts`. Merge Alpha 2 additions (pgvector, device_id, WAL); do not replace the Alpha 1 base.

4. **HITL gates are real**: Every phase ends with a STOP gate. Do not proceed to the next phase without documented owner approval. "Approved in principle" is not approval to execute.

5. **Plan first**: Agents must present a written plan and wait for owner approval before writing any implementation code. Planning documents live in `docs/specs/`.

6. **Cloud engines require explicit activation**: No cloud API credentials are wired without a specific owner approval covering that engine. The presence of a stub or interface definition does not authorize activation.

7. **Never bypass the coordinator**: All evidence operations flow through the coordinator pattern. No direct database writes from tool handlers.

8. **Chain of custody**: SHA-256 at first touch, immutable Pass 1, audit log for every analysis run. Any operation that could break chain of custody requires explicit design review.

9. **Keycloak gates all external exposure**: No service is accessible from outside the Docker network without Keycloak OIDC protection.

10. **Read `docs/INDEX.md` first**: The documentation entrypoint is `docs/INDEX.md`. All architectural context lives there.

---

*Last updated: see git log*
