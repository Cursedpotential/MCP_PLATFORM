# Parity Matrix — MCP Platform Feature Inventory

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Present and working in Alpha 2 |
| 🔄 | Needs restoration from Alpha 1 |
| 🆕 | New capability not in Alpha 1 |
| 🔜 | Planned, not yet started |
| ❌ | Explicitly deferred |
| ⚠️ | Present but needs owner approval before activation |

---

## Document Processing

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| Document intelligence router | Custom pluggable router | 🆕 ⚠️ | Architecture designed, needs owner approval |
| PDF/DOCX/HTML conversion | Pandoc | 🔜 ⚠️ | Local engine, stub exists, needs activation approval |
| OCR — classic | Tesseract | 🔜 ⚠️ | Local engine, stub exists, needs activation approval |
| OCR — neural | DocTR | 🔜 ⚠️ | Local engine, stub only, needs activation approval |
| Document understanding | Docling (IBM) | 🔜 ⚠️ | Local-capable, stub only, needs activation approval |
| OCR — historical | OCRopus | 🔜 ⚠️ | Local engine, stub only, needs activation approval |
| Unstructured doc processing | Unstructured.io | 🔜 ⚠️ | Local or API, stub only, needs activation approval |
| AI-native PDF parsing | LlamaParse | ❌ ⚠️ | Cloud API, deferred until cloud approval |
| Cloud OCR/forms | Google DocAI | ❌ ⚠️ | Cloud API, deferred until cloud approval |
| Cloud OCR/forms | AWS Textract | ❌ ⚠️ | Cloud API, deferred until cloud approval |
| AI vision OCR | GLM-OCR | 🔜 ⚠️ | Local model, planned, needs activation approval |
| Watsonx document understanding | IBM watsonx | ❌ ⚠️ | Cloud API, deferred until cloud approval |

---

## OCR

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| Standard printed text OCR | Tesseract | 🔜 ⚠️ | Stub wired, needs activation approval |
| Neural document OCR | DocTR | 🔜 ⚠️ | Stub only |
| Historical document OCR | OCRopus | 🔜 ⚠️ | Stub only |
| Cloud OCR with form extraction | Google DocAI | ❌ ⚠️ | Deferred, cloud approval required |
| Cloud OCR with table extraction | AWS Textract | ❌ ⚠️ | Deferred, cloud approval required |
| AI-assisted visual OCR | GLM-OCR | 🔜 ⚠️ | Planned, local model, needs approval |

---

## Format Conversion

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| DOCX → Markdown | Pandoc | 🔜 ⚠️ | Stub, needs activation approval |
| HTML → Markdown | Pandoc | 🔜 ⚠️ | Stub, needs activation approval |
| PDF → text | Pandoc + Tesseract | 🔜 ⚠️ | Compound path, stub only |
| EPUB → text | Pandoc | 🔜 ⚠️ | Stub only |
| RTF → text | Pandoc | 🔜 ⚠️ | Stub only |
| CSV/Excel normalization | Custom | 🔜 ⚠️ | Planned |

---

## Parsing — Messaging Formats

| Capability | Format | Status | Notes |
|-----------|--------|--------|-------|
| SMS XML parser | Android SMS Backup & Restore XML | ✅ | Working in Alpha 2 |
| Facebook message parser | Facebook data export JSON | ✅ | Stub present (interface defined) |
| iMessage parser | iMessage SQLite / plist | ✅ | Stub present (interface defined) |
| WhatsApp parser | WhatsApp export TXT | 🔜 ⚠️ | Not yet started |
| Signal parser | Signal export | 🔜 ⚠️ | Not yet started |
| Telegram parser | Telegram export JSON | 🔜 ⚠️ | Not yet started |
| Email parser (MBOX) | RFC 2822 MBOX | 🔜 ⚠️ | Not yet started |

**Note**: Messaging schemas must be ported from Alpha 1 `production-message-schemas.ts` — merge Alpha 2 pgvector/device_id/WAL additions before finalizing.

---

## NLP / Analysis

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| Semantica NLP pipeline | py-mcp-server | ✅ | Integrated |
| Named Entity Recognition (NER) | Semantica | ✅ | Working |
| Text embeddings | sentence-transformers | ✅ | Working |
| Vector indexing | LanceDB | ✅ | Operational |
| Sentiment analysis | Port from Alpha 1 | 🔄 ⚠️ | Needs port + approval |
| Intent classification | Port from Alpha 1 | 🔄 ⚠️ | Needs port + approval |
| HurtLex integration | Alpha 1 → Alpha 2 | 🔄 ⚠️ | Needs port + approval |
| Gaslighting pattern detection | Pass 2 (planned) | 🔜 ⚠️ | Pass 2 scope |
| Contradiction detection | Pass 2 (planned) | 🔜 ⚠️ | Pass 2 scope |
| Temporal reasoning | Neo4j valid_from/valid_to | 🆕 ⚠️ | Needs activation approval |
| Relation extraction | Semantica | ✅ | Working |
| W3C PROV-O provenance | py-mcp-server | 🔜 ⚠️ | Architecture defined, needs implementation approval |

---

## Search

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| Semantic vector search | LanceDB | ✅ | Operational |
| Semantic vector search (fallback) | pgvector (PostgreSQL) | ✅ | Operational |
| Keyword full-text search | PostgreSQL FTS | ✅ | Operational |
| Hybrid search (vector + keyword) | LanceDB + PostgreSQL | 🔜 ⚠️ | Architecture defined, needs implementation approval |
| Graph traversal search | Neo4j Cypher | 🔜 ⚠️ | Neo4j configured, needs population approval |
| Faceted search via Directus | Directus API | 🔜 ⚠️ | Depends on Directus activation |

---

## Vector Database

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| Vector storage + ANN search | LanceDB | ✅ | Embedded, file-based, operational |
| pgvector index | PostgreSQL + pgvector | ✅ | Extension installed, tables created |
| Multi-modal embeddings | Planned | 🔜 ⚠️ | Future capability |

---

## Graph Database

| Capability | Engine | Status | Notes |
|-----------|--------|--------|-------|
| Knowledge graph storage | Neo4j | ⚠️ | Container configured in docker-compose, not yet populated |
| Temporal graph (valid_from/valid_to) | Neo4j | ⚠️ | Schema defined, needs population approval |
| Entity nodes | Neo4j | ⚠️ | NER → Neo4j pipeline designed, needs approval |
| Relation edges | Neo4j | ⚠️ | Relation extraction → Neo4j pipeline designed, needs approval |
| PROV-O provenance graph | Neo4j | 🔜 ⚠️ | Planned, needs approval |

---

## Frontend / UI

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| HITL evidence review chat | React + CopilotKit | ✅ | Stub wired in `client/` |
| Admin/dev chat interface | DIAL Chat | ✅ | Operational |
| Remote chat interface | OpenWebUI | 🔜 ⚠️ | Planned, needs owner approval before activation |
| Remote chat interface (alt) | LibreChat | 🔜 ⚠️ | Planned, needs owner approval before activation |
| Data/admin surface | Directus | ⚠️ | Added to docker-compose, needs activation approval |
| Evidence review UI (Alpha 1 ref) | Alpha 1 React app | 🔄 | Available as reference in MCP_Tool_Platform/ |

---

## Authentication

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| OIDC / OAuth 2.0 provider | Keycloak | ✅ | Operational |
| JWT validation | Keycloak | ✅ | Operational |
| Role-based access control | Keycloak realms | ✅ | Configured |
| Service-to-service auth | Keycloak client credentials | ✅ | Operational |
| MFA | Keycloak (configurable) | ⚠️ | Available, not enforced |

---

## API Layer

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| AI Gateway / model routing | DIAL Core | ✅ | Operational on port 8080 |
| Tool execution — parsers, storage | TS MCP Server | ✅ | Operational on port 8081 |
| Tool execution — NLP, graph | Py MCP Server | ✅ | Operational on port 8082 |
| Tool execution — utilities | JS MCP Server | ✅ | Operational on port 8083 |
| GraphQL federation | WunderGraph Cosmo | ✅ | Operational on port 4000 |
| HTTPS termination + routing | Caddy | ✅ | Operational |

---

## Approval / HITL

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| Review queue | ReviewQueue service | ✅ | Operational |
| HITL review tools | MCP review tools | ✅ | Registered and working |
| CopilotKit chat-based review | React + CopilotKit | ✅ | Stub wired, needs full integration approval |
| Approval audit trail | DuckDB vault | ✅ | Operational |
| Multi-reviewer workflow | Planned | 🔜 ⚠️ | Future capability |

---

## Browser Tools

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| Browser automation / evidence capture | Playwright / Puppeteer | 🔜 ⚠️ | Pending design + approval |
| Screenshot capture | Planned | 🔜 ⚠️ | Pending approval |
| Web archival (WARC) | Planned | 🔜 ⚠️ | Pending approval |

---

## Memory / Context

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| Evidence dedup vault | DuckDB | ✅ | SHA-256 fingerprinting, operational |
| Short-term context store | DuckDB (session) | ✅ | Operational |
| Long-term evidence store | PostgreSQL | ✅ | Operational |
| Memory directory | `memory/` | ✅ | Present in repo |
| Conversation context (AI) | DIAL Core | ✅ | Managed by DIAL |

---

## Orchestration

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| AI model routing + orchestration | DIAL Core | ✅ | Operational |
| Workflow configuration | DIAL workflow config | ✅ | Configured |
| Multi-agent coordination | DIAL Core | ✅ | Operational |
| Tool dispatch | MCP protocol | ✅ | All three MCP servers registered |
| Pipeline scheduling | Planned | 🔜 ⚠️ | No scheduler yet |

---

## Data Surface

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| User-facing data/admin UI | Directus | ⚠️ | Added to docker-compose, **needs activation approval** |
| Evidence table browsing | Directus | ⚠️ | Dependent on Directus activation |
| REST API over PostgreSQL | Directus auto-REST | ⚠️ | Dependent on Directus activation |
| GraphQL over PostgreSQL | Directus auto-GraphQL | ⚠️ | Dependent on Directus activation |
| Export / reporting | Directus | 🔜 ⚠️ | Future, dependent on Directus activation |

---

## Chain of Custody

| Capability | Component | Status | Notes |
|-----------|-----------|--------|-------|
| SHA-256 content fingerprinting | DuckDbVault | ✅ | Applied at first touch |
| Immutable evidence records (Pass 1) | DuckDB WORM flag | ✅ | Operational |
| Audit log per analysis run | PostgreSQL + DuckDB | ✅ | Operational |
| Chain of custody report | Port from Alpha 1 | 🔄 ⚠️ | Alpha 1 has working implementation, needs port + approval |
| Evidence hasher CLI | Port from Alpha 1 | 🔄 ⚠️ | Alpha 1 has working implementation, needs port + approval |
| Legal export package | Planned | 🔜 ⚠️ | Future capability, requires design review |

---

*Last updated: see git log*
