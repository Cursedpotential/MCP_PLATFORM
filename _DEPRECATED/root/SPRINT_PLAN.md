> ⛔ **DEPRECATED — 2026-04-21**: This document contains stale information (DIAL Core referenced as operational, Agno/n8n as planned components). It has been superseded by `GROUND_TRUTH.md`, `MCP_PLATFORM_SYSTEM_PROMPT_V3.md`, and `ORCHESTRATION_CONTRACT.md`. **GROUND_TRUTH.md wins all conflicts.** Preserved for Matt's review — do not follow instructions here that contradict GROUND_TRUTH.md.

---

# Sprint Plan — MCP Platform

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Overview

This sprint plan covers the next major development blocks for the MCP Platform forensic evidence processing stack. Blocks are ordered by dependency, not by priority — priority is set by the owner at each HITL gate.

**Current baseline**: Alpha 2 foundation. Parsers partially wired, storage tiers initialized, DIAL Core operational, Keycloak in place.

---

## Block A: Parser Parity

**Goal**: Bring all three primary messaging parsers to functional parity. SMS is working; Facebook and iMessage stubs must be fleshed out.

| Task | Description | Status | Owner Approval Required |
|------|-------------|--------|------------------------|
| A-01 | Audit SMS XML parser against Alpha 1 production schema | [READY FOR REVIEW] | yes |
| A-02 | Port Alpha 1 `production-message-schemas.ts` field mappings to Alpha 2 | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-03 | Extend SMS parser to handle edge cases (group threads, attachments, reactions) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-04 | Facebook JSON parser — implement full field extraction (stub → working) | [STUB ONLY] | yes |
| A-05 | Facebook parser: map to normalized `EvidenceBatch` output | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-06 | iMessage plist/SQLite parser — implement core extraction (stub → working) | [STUB ONLY] | yes |
| A-07 | iMessage parser: handle attachment metadata, tapback reactions, thread linkage | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-08 | Shared `MessageNormalizer` utility — deduplicate normalization logic across parsers | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-09 | Parser integration tests — round-trip fixture data through each parser | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| A-10 | DuckDB dedup check for all three parsers (SHA-256 fingerprint before insert) | [PLANNED - NEEDS OWNER APPROVAL] | yes |

**HITL Gate A**: Owner reviews parser output samples before Block B begins.

---

## Block B: Embedding + LanceDB Wiring

**Goal**: Wire the embedding pipeline so that ingested evidence produces searchable vectors in LanceDB.

| Task | Description | Status | Owner Approval Required |
|------|-------------|--------|------------------------|
| B-01 | Confirm LanceDB table schema matches Alpha 2 vector spec | [READY FOR REVIEW] | yes |
| B-02 | Select embedding model — confirm local (sentence-transformers) vs. remote | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-03 | Implement `EmbeddingService` in py-mcp-server | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-04 | Wire `EmbeddingService` to post-parse pipeline in ts-mcp-server | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-05 | LanceDB write path — batch upsert with UUIDv7 primary keys | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-06 | Semantic search tool — `evidence_search` MCP tool returning ranked results | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-07 | pgvector fallback — ensure PostgreSQL can serve semantic queries if LanceDB unavailable | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| B-08 | Embedding pipeline performance test — target throughput for batch ingestion | [PLANNED - NEEDS OWNER APPROVAL] | yes |

**HITL Gate B**: Owner verifies search results on a known fixture before Block C begins.

---

## Block C: Pass 1 Analysis Pipeline

**Goal**: Implement the immutable 24-hour context window analysis (Pass 1). This is the WORM pass — once written, it cannot be modified.

| Task | Description | Status | Owner Approval Required |
|------|-------------|--------|------------------------|
| C-01 | Finalize Pass 1 schema in PostgreSQL (sentiment, intent, entities, window metadata) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-02 | Port sentiment analysis from Alpha 1 pattern analyzer | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-03 | Port HurtLex integration from Alpha 1 | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-04 | Implement NER extraction via Semantica (named entities → PostgreSQL + Neo4j) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-05 | 24-hour window partitioning logic | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-06 | WORM enforcement — Pass 1 records get immutable flag in DuckDB vault | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-07 | `run_pass1_analysis` MCP tool implementation | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-08 | Pass 1 output audit log (chain of custody entry per analysis run) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| C-09 | Unit tests for Pass 1 pipeline | [PLANNED - NEEDS OWNER APPROVAL] | yes |

**HITL Gate C**: Owner reviews Pass 1 output on real or representative fixture data before Block D begins.

---

## Block D: MCP Tool Registration

**Goal**: Register the three primary forensic tools as callable MCP tools accessible through DIAL Core.

| Task | Description | Status | Owner Approval Required |
|------|-------------|--------|------------------------|
| D-01 | `ingest_evidence` tool — accepts file path or raw content, routes to correct parser | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-02 | `ingest_evidence` — validates SHA-256, checks DuckDB dedup, writes to PostgreSQL | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-03 | `run_pass1_analysis` tool — triggers Pass 1 pipeline for a given evidence batch ID | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-04 | `evidence_search` tool — semantic + keyword search across LanceDB + pgvector | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-05 | Tool registration in ts-mcp-server tool manifest | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-06 | Tool registration in py-mcp-server tool manifest | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-07 | DIAL Core routing config for new tools | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-08 | Integration test — call all three tools end-to-end via DIAL Core | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| D-09 | Tool error handling and structured error responses | [PLANNED - NEEDS OWNER APPROVAL] | yes |

**HITL Gate D**: Owner approves tool signatures and test results before Block E begins.

---

## Block E: Directus Data Surface + Document Intelligence Architecture

**Goal**: Activate Directus as the user-facing data/admin surface, and lay the architectural foundation for multi-engine document intelligence.

| Task | Description | Status | Owner Approval Required |
|------|-------------|--------|------------------------|
| E-01 | Directus — confirm docker-compose service definition is correct | [READY FOR REVIEW] | yes |
| E-02 | Directus — activate service (start container, verify health) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-03 | Directus — configure PostgreSQL connection to Alpha 2 database | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-04 | Directus — expose evidence tables as read-only data surfaces | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-05 | Directus — role-based access control setup (admin vs. reviewer) | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-06 | Document intelligence router — define pluggable `EngineRouter` interface | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-07 | Pandoc engine stub → working local implementation | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-08 | Tesseract OCR engine stub → working local implementation | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-09 | DocTR engine stub (local neural OCR) | [STUB ONLY] | yes |
| E-10 | Docling engine stub (IBM document understanding) | [STUB ONLY] | yes |
| E-11 | Cloud engine interface contracts (Google DocAI, AWS Textract, LlamaParse) — interface only, no activation | [PLANNED - NEEDS OWNER APPROVAL] | yes |
| E-12 | Engine fallback chain configuration | [PLANNED - NEEDS OWNER APPROVAL] | yes |

**HITL Gate E**: Owner reviews Directus UI surface and engine router design before any cloud credentials are wired.

---

## UI Assets

### Alpha 1 UI Code
The Alpha 1 codebase contains a working React-based evidence review interface. Before building any new UI components, agents must audit `MCP_Tool_Platform/` for reusable UI patterns, components, and state management logic. Do not duplicate what already exists.

### CopilotKit React Chat Module
- Location: `client/` directory
- Status: Stub wired, not fully integrated
- Purpose: Human-in-the-loop (HITL) evidence review chat interface
- Activation: **Requires explicit owner approval**
- Integration point: DIAL Core via MCP tool calls

### OpenWebUI Integration
- Status: [PLANNED - NEEDS OWNER APPROVAL]
- Role: Remote chat interface federating into DIAL Core
- Deployment: Docker container, Caddy-routed
- Activation gate: Owner must approve before any OpenWebUI container is started or configured

### LibreChat Integration
- Status: [PLANNED - NEEDS OWNER APPROVAL]
- Role: Alternative remote chat interface with document upload support
- Deployment: Docker container, Caddy-routed
- Activation gate: Owner must approve before any LibreChat container is started or configured

---

## Risk and Rollback

| Risk | Likelihood | Mitigation | Rollback |
|------|-----------|------------|---------|
| Messaging schema port breaks existing SMS parser | Medium | Port to new module, keep old module untouched until tests pass | Revert import, keep old module |
| LanceDB write performance degrades at scale | Low | Benchmark at Block B, add batch size config | Switch to pgvector-only until resolved |
| Directus migration conflicts with PostgreSQL schema | Medium | Run Directus against a read replica or non-destructive schema | Stop Directus container, no data loss |
| Cloud engine credentials accidentally committed | High | Pre-push secret scan (`scripts/git/prepush-check.sh`), `.env` in `.gitignore` | Rotate credentials immediately |
| Pass 1 WORM records corrupted | Low | Dual-write: DuckDB immutable flag + PostgreSQL audit log | Restore from DuckDB vault (source of truth) |
| OpenWebUI/LibreChat expose unauthenticated endpoints | Medium | Gate behind Keycloak OIDC before any external exposure | Stop container immediately |

---

## What Is NOT In Scope

The following are explicitly out of scope for this sprint plan and require separate owner authorization:

- **Pass 2 analysis** (longitudinal, contradiction detection, gaslighting patterns)
- **Any production deployment** (all work is dev/staging only)
- **Cloud engine activation** (Google DocAI, AWS Textract, LlamaParse) — stubs only
- **SurrealDB** (deferred, see ADR-022)
- **Any external data egress** beyond the defined storage tiers
- **New authentication providers** beyond Keycloak
- **Mobile clients**
- **Automated legal document generation**

---

## HITL Gates Summary

| Gate | Trigger | Who Approves |
|------|---------|-------------|
| Gate A | Parser output samples ready for review | Owner |
| Gate B | Semantic search results verified on fixture | Owner |
| Gate C | Pass 1 output verified on real/representative data | Owner |
| Gate D | Tool signatures and integration test results | Owner |
| Gate E | Directus UI surface + engine router design | Owner |
| Gate F (pre-cloud) | Any cloud engine credential wiring | Owner |
| Gate G (pre-UI deploy) | OpenWebUI / LibreChat container activation | Owner |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| [PLANNED - NEEDS OWNER APPROVAL] | Designed, not started, explicit approval required before starting |
| [STUB ONLY] | Skeleton exists in code, no real implementation |
| [READY FOR REVIEW] | Work exists and is ready for owner review before proceeding |
| [IN PROGRESS] | Actively being worked (requires owner to have approved) |
| [COMPLETE] | Done and verified |

---

*Last updated: see git log*
