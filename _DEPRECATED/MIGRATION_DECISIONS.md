# Migration Decisions — MCP Platform

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Purpose

This document records the per-capability migration decisions as Alpha 1 capabilities are evaluated for inclusion in Alpha 2. Each entry documents what was decided, why, where the source lives, and whether owner approval is required before execution.

---

## Decision Table Format

Each section contains a table with:
- **Decision**: What action is being taken
- **Rationale**: Why this decision was made
- **Source**: Where the capability originates (Alpha 1 / Alpha 2 / New)
- **Status**: Current disposition
- **Needs Owner Approval**: Whether explicit approval is required before execution
- **Notes**: Additional context

---

## Document Processing

### Document Intelligence Router

| Field | Value |
|-------|-------|
| **Decision** | Build a new pluggable `EngineRouter` in Alpha 2 — not ported from Alpha 1 (Alpha 1 had no multi-engine router) |
| **Rationale** | Alpha 1 used ad-hoc document handling. Alpha 2 requires a clean abstraction layer supporting 11+ engines with fallback chains and cost/privacy routing |
| **Source** | New |
| **Status** | Architecture designed; implementation not started |
| **Needs Owner Approval** | Yes — before any engine is registered or invoked |
| **Notes** | See `docs/architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md` for full design |

### Pandoc (Format Conversion)

| Field | Value |
|-------|-------|
| **Decision** | Implement as a local engine in the document intelligence router |
| **Rationale** | Pandoc is open source, local-only, no API costs, broad format support (DOCX, HTML, RTF, EPUB → Markdown/text) |
| **Source** | New (Alpha 1 did not use Pandoc directly) |
| **Status** | Stub exists; full implementation needs owner approval |
| **Needs Owner Approval** | Yes |
| **Notes** | Pandoc binary must be available in the Docker image; no network calls |

### Tesseract OCR

| Field | Value |
|-------|-------|
| **Decision** | Implement as a local OCR engine in the document intelligence router |
| **Rationale** | Tesseract is open source, battle-tested, no API costs, works offline |
| **Source** | New for Alpha 2 |
| **Status** | Stub exists; full implementation needs owner approval |
| **Needs Owner Approval** | Yes |
| **Notes** | Tesseract binary must be in Docker image; GPU acceleration optional |

### DocTR (Neural OCR)

| Field | Value |
|-------|-------|
| **Decision** | Include as a local neural OCR engine; stub only until approved |
| **Rationale** | DocTR provides significantly better accuracy than Tesseract on degraded or handwritten documents |
| **Source** | New |
| **Status** | Stub only |
| **Needs Owner Approval** | Yes — model download and inference infrastructure required |
| **Notes** | Model weights must be approved for inclusion in the Docker image |

### Docling (IBM Document Understanding)

| Field | Value |
|-------|-------|
| **Decision** | Include as a local engine stub; activate only with approval |
| **Rationale** | Docling provides rich document structure understanding (tables, figures, sections) beyond basic OCR |
| **Source** | New |
| **Status** | Stub only |
| **Needs Owner Approval** | Yes |
| **Notes** | Can run locally; IBM licensing terms should be reviewed before activation |

### OCRopus (Historical Document OCR)

| Field | Value |
|-------|-------|
| **Decision** | Include as a local engine stub for historical or degraded document processing |
| **Rationale** | OCRopus is specialized for historical documents where Tesseract underperforms |
| **Source** | New |
| **Status** | Stub only |
| **Needs Owner Approval** | Yes |
| **Notes** | Niche use case; activate only when working with historical evidence |

### Unstructured.io

| Field | Value |
|-------|-------|
| **Decision** | Include as a local engine stub; can run fully offline or via their API |
| **Rationale** | Unstructured provides excellent multi-format extraction including email, presentation slides, spreadsheets |
| **Source** | New |
| **Status** | Stub only |
| **Needs Owner Approval** | Yes — local vs. API mode decision required |
| **Notes** | If API mode selected, credentials required and cloud approval gate applies |

### LlamaParse (AI-Native PDF Parsing)

| Field | Value |
|-------|-------|
| **Decision** | Deferred — cloud API, requires LlamaCloud credentials |
| **Rationale** | High capability for complex PDFs, but requires external API calls. Deferred until cloud approval gate is passed |
| **Source** | New |
| **Status** | Deferred |
| **Needs Owner Approval** | Yes — cloud activation approval required |
| **Notes** | Do not wire credentials until owner explicitly approves cloud engine activation |

### Google DocAI

| Field | Value |
|-------|-------|
| **Decision** | Deferred — cloud API, requires GCP credentials |
| **Rationale** | Best-in-class for forms and structured documents, but involves data egress to Google. Deferred until cloud approval |
| **Source** | New |
| **Status** | Deferred |
| **Needs Owner Approval** | Yes — cloud activation approval required |
| **Notes** | Data privacy implications must be reviewed before activation. Never activate without explicit owner approval |

### AWS Textract

| Field | Value |
|-------|-------|
| **Decision** | Deferred — cloud API, requires AWS credentials |
| **Rationale** | Strong table extraction capability, but involves data egress to AWS. Deferred until cloud approval |
| **Source** | New |
| **Status** | Deferred |
| **Needs Owner Approval** | Yes — cloud activation approval required |
| **Notes** | Data privacy implications must be reviewed. Never activate without explicit owner approval |

### GLM-OCR

| Field | Value |
|-------|-------|
| **Decision** | Include as a planned local AI-vision OCR engine; no implementation yet |
| **Rationale** | GLM-based visual OCR provides multimodal understanding of document images |
| **Source** | New |
| **Status** | Planned (no stub) |
| **Needs Owner Approval** | Yes — model weights and inference infrastructure required |
| **Notes** | Requires significant GPU resources; evaluate hardware availability before planning |

### IBM watsonx

| Field | Value |
|-------|-------|
| **Decision** | Deferred — cloud API, requires IBM Cloud credentials |
| **Rationale** | Enterprise document intelligence capability, but involves data egress and licensing costs. Deferred |
| **Source** | New |
| **Status** | Deferred |
| **Needs Owner Approval** | Yes — cloud activation approval required |
| **Notes** | IBM licensing and data processing terms must be reviewed before activation |

---

## Messaging Parsers / Schemas

### SMS XML Parser

| Field | Value |
|-------|-------|
| **Decision** | Keep and extend the Alpha 2 SMS parser; validate against Alpha 1 production schemas |
| **Rationale** | SMS parser is working in Alpha 2. Alpha 1 `production-message-schemas.ts` has battle-tested field definitions |
| **Source** | Alpha 2 (working) + Alpha 1 (schema reference) |
| **Status** | Working; schema validation against Alpha 1 needs approval |
| **Needs Owner Approval** | Yes — any schema changes require approval |
| **Notes** | Port field mapping logic from Alpha 1 `production-message-schemas.ts`; do not break the existing working parser |

### Facebook Message Parser

| Field | Value |
|-------|-------|
| **Decision** | Port from Alpha 1 production-message-schemas.ts — merge in Alpha 2 pgvector/device_id/WAL additions |
| **Rationale** | Alpha 1 has proven Facebook JSON parsing logic. Alpha 2 needs the pgvector embedding fields and device_id tracking that did not exist in Alpha 1 |
| **Source** | Alpha 1 (core logic) + Alpha 2 (schema extensions) |
| **Status** | Stub in Alpha 2; port from Alpha 1 needs owner approval |
| **Needs Owner Approval** | Yes |
| **Notes** | Merge strategy: Alpha 1 field extractors + Alpha 2 normalized output schema. Test with real Facebook export fixture |

### iMessage Parser

| Field | Value |
|-------|-------|
| **Decision** | Port from Alpha 1 production-message-schemas.ts — merge in Alpha 2 pgvector/device_id/WAL additions |
| **Rationale** | Same rationale as Facebook parser — Alpha 1 has working iMessage SQLite/plist extraction logic |
| **Source** | Alpha 1 (core logic) + Alpha 2 (schema extensions) |
| **Status** | Stub in Alpha 2; port from Alpha 1 needs owner approval |
| **Needs Owner Approval** | Yes |
| **Notes** | iMessage parser must handle both SQLite (chat.db) and plist exports. Tapback reactions and thread grouping must be preserved |

---

## NLP / Analysis

### Semantica Pipeline

| Field | Value |
|-------|-------|
| **Decision** | Keep and extend the Alpha 2 Semantica pipeline |
| **Rationale** | Semantica is working in Alpha 2 and provides NER, relation extraction, and embeddings |
| **Source** | Alpha 2 |
| **Status** | Operational |
| **Needs Owner Approval** | No — for existing functionality. Yes — for any new pipeline stages |
| **Notes** | Any extensions to the pipeline (new models, new extraction types) require approval |

### Sentiment Analysis

| Field | Value |
|-------|-------|
| **Decision** | Port from Alpha 1 pattern analyzer |
| **Rationale** | Alpha 1 has a working sentiment analysis implementation. No reason to rewrite |
| **Source** | Alpha 1 |
| **Status** | Not yet ported |
| **Needs Owner Approval** | Yes |
| **Notes** | Port to py-mcp-server. Do not modify the Alpha 1 source |

### HurtLex Integration

| Field | Value |
|-------|-------|
| **Decision** | Port from Alpha 1 |
| **Rationale** | HurtLex integration was built and tested in Alpha 1. Reuse the proven implementation |
| **Source** | Alpha 1 |
| **Status** | Not yet ported |
| **Needs Owner Approval** | Yes |
| **Notes** | HurtLex lexicon files must be available in the py-mcp-server container |

### Pass 1 Analysis Pipeline

| Field | Value |
|-------|-------|
| **Decision** | New implementation using Alpha 1 as reference |
| **Rationale** | Pass 1 is a new capability (24-hour window, WORM) that did not exist in exactly this form in Alpha 1. Alpha 1's analysis components are used as building blocks |
| **Source** | New (built on Alpha 1 components) |
| **Status** | Not yet started |
| **Needs Owner Approval** | Yes — before any Pass 1 records are written |
| **Notes** | WORM enforcement is critical. Incorrect implementation could corrupt chain of custody |

---

## Storage

### DuckDB Vault

| Field | Value |
|-------|-------|
| **Decision** | Keep Alpha 2 DuckDbVault as-is |
| **Rationale** | Working and tested. SHA-256 fingerprinting and WORM flags are operational |
| **Source** | Alpha 2 |
| **Status** | Operational |
| **Needs Owner Approval** | No — for existing functionality |
| **Notes** | Schema changes require approval |

### PostgreSQL Evidence Store

| Field | Value |
|-------|-------|
| **Decision** | Keep Alpha 2 schema; port Alpha 1 relation structure where superior |
| **Rationale** | Alpha 2 schema includes pgvector, device_id, WAL fields that Alpha 1 lacked. Alpha 1 had better normalized evidence relations |
| **Source** | Alpha 2 (primary) + Alpha 1 (reference) |
| **Status** | Operational |
| **Needs Owner Approval** | Yes — for any schema migrations |
| **Notes** | Run all schema changes through migration scripts in `migrations/` |

### LanceDB

| Field | Value |
|-------|-------|
| **Decision** | Keep and extend Alpha 2 LanceDB integration |
| **Rationale** | LanceDB is operational and provides fast local vector search |
| **Source** | Alpha 2 |
| **Status** | Operational |
| **Needs Owner Approval** | No — for existing tables. Yes — for new tables or schema changes |
| **Notes** | Table schema changes require migration tooling |

### Neo4j

| Field | Value |
|-------|-------|
| **Decision** | Keep configured, delay population until NER pipeline is approved |
| **Rationale** | Neo4j container is configured but no graph data exists yet. Premature population would create incorrect provenance chains |
| **Source** | Alpha 2 |
| **Status** | Configured, not populated |
| **Needs Owner Approval** | Yes — before any nodes or edges are written |
| **Notes** | Graph population is gated on NER pipeline approval |

---

## Frontend / UI

### CopilotKit React Module

| Field | Value |
|-------|-------|
| **Decision** | Keep stub, complete integration with owner approval |
| **Rationale** | CopilotKit provides the HITL evidence review chat interface. Stub is in place |
| **Source** | Alpha 2 |
| **Status** | Stub wired |
| **Needs Owner Approval** | Yes — before full integration |
| **Notes** | Alpha 1 UI components in `MCP_Tool_Platform/` should be reviewed for reuse before building new components |

### OpenWebUI

| Field | Value |
|-------|-------|
| **Decision** | Plan integration as a remote chat interface; do not activate without approval |
| **Rationale** | OpenWebUI provides a mature open-source chat interface that can federate with DIAL Core |
| **Source** | New |
| **Status** | Planned |
| **Needs Owner Approval** | Yes — before any container is started |
| **Notes** | Must be gated behind Keycloak OIDC before any external exposure |

### LibreChat

| Field | Value |
|-------|-------|
| **Decision** | Plan integration as alternative remote chat interface; do not activate without approval |
| **Rationale** | LibreChat offers document upload support and multi-model routing that complements DIAL Core |
| **Source** | New |
| **Status** | Planned |
| **Needs Owner Approval** | Yes — before any container is started |
| **Notes** | Must be gated behind Keycloak OIDC. Docker compose service definition should be reviewed before activation |

### Directus

| Field | Value |
|-------|-------|
| **Decision** | Activate Directus as user-facing data/admin surface with owner approval |
| **Rationale** | Directus provides a no-code data browser and REST/GraphQL layer over PostgreSQL that reduces custom UI development |
| **Source** | New |
| **Status** | Added to docker-compose; not yet activated |
| **Needs Owner Approval** | Yes — before container is started |
| **Notes** | Directus must connect to PostgreSQL in read-only or controlled-write mode for evidence tables. Admin tables can be read-write |

---

## Auth / Security

### Keycloak

| Field | Value |
|-------|-------|
| **Decision** | Keep and extend the Alpha 2 Keycloak configuration |
| **Rationale** | Keycloak is operational and provides OIDC/JWT for all services |
| **Source** | Alpha 2 |
| **Status** | Operational |
| **Needs Owner Approval** | No — for existing configuration. Yes — for new realms, clients, or MFA enforcement |
| **Notes** | All new services must register as Keycloak clients before activation |

---

## Deferred / Rejected

### SurrealDB

| Field | Value |
|-------|-------|
| **Decision** | Deferred for future evaluation (see ADR-022) |
| **Rationale** | SurrealDB's multi-model capabilities are interesting but not needed for current phase. Adding a fifth database technology would increase operational complexity |
| **Source** | N/A |
| **Status** | Deferred |
| **Needs Owner Approval** | Yes — if ever reconsidered |
| **Notes** | Re-evaluate if a specific use case emerges that cannot be served by DuckDB + PostgreSQL + LanceDB + Neo4j |

---

*Last updated: see git log*
