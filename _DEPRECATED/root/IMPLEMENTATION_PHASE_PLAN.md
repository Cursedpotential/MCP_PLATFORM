> ⛔ **DEPRECATED — 2026-04-21**: This document contains stale information (DIAL Core referenced as operational, Agno/n8n as planned components). It has been superseded by `GROUND_TRUTH.md`, `MCP_PLATFORM_SYSTEM_PROMPT_V3.md`, and `ORCHESTRATION_CONTRACT.md`. **GROUND_TRUTH.md wins all conflicts.** Preserved for Matt's review — do not follow instructions here that contradict GROUND_TRUTH.md.

---

# Implementation Phase Plan — MCP Platform

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Overview

This document breaks the platform development into discrete phases with explicit owner approval gates between each phase. No phase may begin without documented owner approval of the preceding phase's outputs.

**Complexity indicators**: [S] Small (< 1 day), [M] Medium (1–3 days), [L] Large (3–7 days), [XL] Extra Large (> 7 days)

---

## Phase 0: Foundation Audit

**Objective**: Establish a clean, verified baseline before any new work begins.

> 🛑 **STOP — Owner approval required before Phase 1 begins.**

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 0-01 | [S] | Audit `MCP_Tool_Platform/` — catalog all reusable Alpha 1 assets | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-02 | [S] | Verify all storage tiers are healthy (DuckDB, PostgreSQL, LanceDB, Neo4j container) | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-03 | [S] | Verify all MCP servers are responding (health checks on 8081, 8082, 8083) | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-04 | [S] | Verify DIAL Core routing (8080) and Keycloak auth (8180) | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-05 | [M] | Run existing test suites — establish baseline pass/fail counts | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-06 | [S] | Document Alpha 1 asset inventory in `docs/specs/alpha1-inventory.md` | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-07 | [S] | Confirm `production-message-schemas.ts` is present and readable in Alpha 1 | [PLANNED - NEEDS OWNER APPROVAL] |
| 0-08 | [S] | Confirm DuckDB vault is initialized and SHA-256 fingerprinting works end-to-end | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 0 Outputs**:
- Alpha 1 asset inventory document
- Health check report for all tiers
- Baseline test results

**Owner Approval Gate**: Owner reviews outputs and explicitly approves Phase 1 kickoff.

---

## Phase 1: Core Ingestion + Directus + Document Intelligence Foundation

**Objective**: Complete the ingestion pipeline, activate Directus, port messaging schemas, and implement the first working local document intelligence engines.

> 🛑 **STOP — Owner approval required before Phase 1 begins.**
> 🛑 **STOP — Owner approval required before Phase 2 begins.**

### 1.1 Directus Activation

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 1.1-01 | [S] | Review Directus docker-compose service definition for correctness | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-02 | [S] | Start Directus container and verify health | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-03 | [M] | Configure Directus PostgreSQL connection (read-only for evidence tables) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-04 | [M] | Configure Directus RBAC (admin role, reviewer role) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-05 | [S] | Register Directus as a Keycloak OIDC client | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-06 | [S] | Expose Directus via Caddy at `/admin` | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.1-07 | [S] | Smoke test: verify evidence tables are browsable in Directus UI | [PLANNED - NEEDS OWNER APPROVAL] |

### 1.2 Messaging Schema Port from Alpha 1

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 1.2-01 | [M] | Read and document all field definitions in Alpha 1 `production-message-schemas.ts` | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.2-02 | [L] | Port SMS schema: Alpha 1 fields + Alpha 2 extensions (pgvector, device_id, WAL) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.2-03 | [L] | Port Facebook schema: Alpha 1 fields + Alpha 2 extensions | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.2-04 | [L] | Port iMessage schema: Alpha 1 fields + Alpha 2 extensions | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.2-05 | [M] | Write migration scripts for any PostgreSQL schema changes | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.2-06 | [M] | Validate SMS parser still passes all existing tests after schema changes | [PLANNED - NEEDS OWNER APPROVAL] |

### 1.3 Facebook and iMessage Parsers (Stub → Working)

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 1.3-01 | [L] | Implement Facebook JSON parser full field extraction | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.3-02 | [M] | Map Facebook parser output to normalized `EvidenceBatch` | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.3-03 | [L] | Implement iMessage SQLite/plist parser full field extraction | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.3-04 | [M] | Map iMessage parser output to normalized `EvidenceBatch` | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.3-05 | [M] | Add `MessageNormalizer` shared utility (dedup normalization logic) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.3-06 | [M] | Integration tests for Facebook and iMessage parsers against fixture data | [PLANNED - NEEDS OWNER APPROVAL] |

### 1.4 Document Intelligence Local Engines

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 1.4-01 | [M] | Define `EngineRouter` interface and base class | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.4-02 | [M] | Implement Pandoc engine (DOCX, HTML, RTF, EPUB → Markdown/text) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.4-03 | [M] | Implement Tesseract OCR engine (image → text) | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.4-04 | [M] | Implement fallback chain: Pandoc → Tesseract → error | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.4-05 | [S] | Add Pandoc and Tesseract to TS/Py MCP Docker images | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.4-06 | [M] | Integration tests: route sample documents through Pandoc and Tesseract | [PLANNED - NEEDS OWNER APPROVAL] |

### 1.5 Embedding Pipeline Wiring

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 1.5-01 | [M] | Confirm sentence-transformers model selection with owner | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.5-02 | [L] | Implement `EmbeddingService` in py-mcp-server | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.5-03 | [M] | Wire embedding pipeline to post-parse ingestion path | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.5-04 | [M] | LanceDB batch upsert write path | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.5-05 | [S] | pgvector fallback write path | [PLANNED - NEEDS OWNER APPROVAL] |
| 1.5-06 | [M] | Register `evidence_search` MCP tool (semantic search) | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 1 Outputs**:
- Directus operational
- Messaging schemas ported from Alpha 1
- Facebook and iMessage parsers working
- Pandoc and Tesseract engines operational
- `evidence_search` tool registered and working

**Owner Approval Gate**: Owner reviews Phase 1 outputs, tests search on fixture data, and explicitly approves Phase 2 kickoff.

---

## Phase 2: Engine Expansion + Cloud Provider Integration

**Objective**: Activate additional document intelligence engines and integrate OpenWebUI/LibreChat (if approved).

> 🛑 **STOP — Owner approval required before Phase 2 begins.**
> 🛑 **STOP — Owner approval required before Phase 3 begins.**

### 2.1 Local Engine Expansion

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 2.1-01 | [L] | Implement DocTR neural OCR engine | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.1-02 | [L] | Implement Docling document understanding engine | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.1-03 | [M] | Implement OCRopus historical document engine | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.1-04 | [L] | Implement Unstructured.io engine (local mode) | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.1-05 | [M] | Update fallback chain for all local engines | [PLANNED - NEEDS OWNER APPROVAL] |

### 2.2 Cloud Engine Integration (Conditional on Owner Approval)

> ⚠️ **Each cloud engine requires individual owner approval before wiring credentials.**

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 2.2-01 | [M] | Implement LlamaParse cloud engine client | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.2-02 | [M] | Implement Google DocAI cloud engine client | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.2-03 | [M] | Implement AWS Textract cloud engine client | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.2-04 | [M] | Implement IBM watsonx cloud engine client | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.2-05 | [S] | Cloud engine credential injection via environment variables (never hardcoded) | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.2-06 | [M] | Cost/privacy routing: only route to cloud if local engines failed and cloud is explicitly allowed | [PLANNED - NEEDS OWNER APPROVAL] |

### 2.3 Neo4j Population

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 2.3-01 | [L] | NER extraction → Neo4j entity nodes | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.3-02 | [L] | Relation extraction → Neo4j edges | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.3-03 | [M] | Temporal facts → valid_from/valid_to properties | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.3-04 | [M] | PROV-O provenance chain implementation | [PLANNED - NEEDS OWNER APPROVAL] |

### 2.4 OpenWebUI + LibreChat (Conditional on Owner Approval)

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 2.4-01 | [M] | Add OpenWebUI docker-compose service definition | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.4-02 | [M] | Configure OpenWebUI → DIAL Core routing | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.4-03 | [S] | Register OpenWebUI as Keycloak OIDC client | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.4-04 | [M] | Add LibreChat docker-compose service definition | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.4-05 | [M] | Configure LibreChat → DIAL Core routing | [PLANNED - NEEDS OWNER APPROVAL] |
| 2.4-06 | [S] | Register LibreChat as Keycloak OIDC client | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 2 Outputs**:
- All approved local engines operational
- Any approved cloud engines operational (with audited credentials)
- Neo4j populated from NER pipeline
- OpenWebUI and/or LibreChat operational (if approved)

**Owner Approval Gate**: Owner reviews Phase 2 outputs and explicitly approves Phase 3 kickoff.

---

## Phase 3: Pass 1 Full Analysis Pipeline

**Objective**: Implement the complete Pass 1 immutable analysis pipeline.

> 🛑 **STOP — Owner approval required before Phase 3 begins.**
> 🛑 **STOP — Owner approval required before Phase 4 begins.**

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 3-01 | [M] | Finalize Pass 1 PostgreSQL schema (sentiment, intent, entities, window metadata) | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-02 | [L] | Port sentiment analysis from Alpha 1 pattern analyzer | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-03 | [L] | Port intent classification from Alpha 1 | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-04 | [L] | Port HurtLex integration from Alpha 1 | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-05 | [L] | Implement 24-hour window partitioning logic | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-06 | [M] | WORM enforcement — Pass 1 immutable flag in DuckDB | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-07 | [M] | Register `run_pass1_analysis` MCP tool | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-08 | [M] | Pass 1 audit log (chain of custody entry per run) | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-09 | [L] | Unit and integration tests for Pass 1 pipeline | [PLANNED - NEEDS OWNER APPROVAL] |
| 3-10 | [M] | Register `ingest_evidence` MCP tool (full pipeline: parse → fingerprint → embed → Pass 1) | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 3 Outputs**:
- Pass 1 pipeline operational with WORM enforcement
- All three MCP tools registered: `ingest_evidence`, `run_pass1_analysis`, `evidence_search`
- Pass 1 output verified on representative fixture data

**Owner Approval Gate**: Owner reviews Pass 1 output quality and chain of custody audit trail.

---

## Phase 4: HITL Review UI + CopilotKit Integration

**Objective**: Complete the human-in-the-loop review interface for evidence annotation and approval.

> 🛑 **STOP — Owner approval required before Phase 4 begins.**
> 🛑 **STOP — Owner approval required before Phase 5 begins.**

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 4-01 | [L] | Audit Alpha 1 review UI components for reuse | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-02 | [XL] | Complete CopilotKit React module integration | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-03 | [L] | Evidence review workflow (accept / reject / annotate) | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-04 | [M] | Review decision audit trail (who approved what, when) | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-05 | [L] | ReviewQueue UI integration (queue display, priority ordering) | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-06 | [M] | Chain of custody display in review UI | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-07 | [M] | Multi-reviewer support (if approved) | [PLANNED - NEEDS OWNER APPROVAL] |
| 4-08 | [L] | End-to-end HITL test: ingest → Pass 1 → review queue → approval | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 4 Outputs**:
- CopilotKit HITL review UI operational
- Review decisions recorded with full audit trail
- End-to-end workflow verified

**Owner Approval Gate**: Owner completes a review session on fixture data and approves UI design.

---

## Phase 5: Production Hardening

**Objective**: Prepare the platform for production use.

> 🛑 **STOP — Owner approval required before Phase 5 begins.**
> 🛑 **STOP — Owner approval required before any production deployment.**

| Task | Complexity | Description | Status |
|------|-----------|-------------|--------|
| 5-01 | [L] | Performance testing — ingestion throughput benchmarks | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-02 | [L] | Security review — penetration testing scope definition | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-03 | [L] | Backup and recovery procedures for all storage tiers | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-04 | [M] | Operational runbooks (startup, shutdown, recovery, evidence export) | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-05 | [M] | Monitoring and alerting setup (metrics, log aggregation) | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-06 | [L] | Secrets rotation procedures | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-07 | [XL] | Production deployment architecture design | [PLANNED - NEEDS OWNER APPROVAL] |
| 5-08 | [M] | Data retention and deletion policies | [PLANNED - NEEDS OWNER APPROVAL] |

**Phase 5 Outputs**:
- Platform hardened for production
- Runbooks complete
- Monitoring operational
- Production deployment plan approved

**Owner Approval Gate**: Owner reviews all Phase 5 outputs and explicitly approves production deployment.

---

## Phase Gate Summary

| Gate | Trigger | Required Before |
|------|---------|----------------|
| Phase 0 → 1 | Phase 0 outputs reviewed | Phase 1 may begin |
| Phase 1 → 2 | Phase 1 outputs reviewed, search verified on fixture | Phase 2 may begin |
| Phase 2 → 3 | Phase 2 outputs reviewed | Phase 3 may begin |
| Phase 3 → 4 | Pass 1 output quality and CoC trail verified | Phase 4 may begin |
| Phase 4 → 5 | HITL review session completed on fixture data | Phase 5 may begin |
| Phase 5 → Production | All Phase 5 outputs reviewed | Production deployment may begin |

---

*Last updated: see git log*
