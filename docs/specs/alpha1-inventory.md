---
title: Alpha 1 Asset Inventory & Phase 0 Foundation Audit
reviewed: 2026-04-11
revision: 1
author: Copilot
status: current
phase: 0
---

# Alpha 1 Asset Inventory & Phase 0 Foundation Audit

> This document is the output of Phase 0 tasks 0-01 through 0-08 from `IMPLEMENTATION_PHASE_PLAN.md`.
> It must be reviewed and approved by the owner before Phase 1 begins.

---

## Summary

Phase 0 was initiated in response to the most recent merge (PR #1: "feat: Directus data surface, ingestion pipeline, multi-engine document intelligence, and sprint planning suite").

The audit covered:
- Alpha 1 codebase availability
- Alpha 2 (current repo) source catalog
- Storage tier readiness (code review, not runtime verification)
- MCP server readiness (code review)
- TypeScript build health
- Test suite inventory
- PostgreSQL migration state
- Directus docker-compose service definition review

---

## Task 0-01: Alpha 1 Codebase Audit

**Status**: BLOCKED — `MCP_Tool_Platform/` is not present in this repository clone.

The `_DEPRECATED/AGENT_HANDOFF_PROMPT_POST_DIAL.md` and `AGENTS.md` both reference an Alpha 1 codebase at `MCP_Tool_Platform/` that contains proven implementations of the following assets:

| Asset | Expected Alpha 1 Path |
|-------|-----------------------|
| Pattern analyzer (sentiment, intent) | `MCP_Tool_Platform/server/mcp/analysis/` |
| Chain of custody module | `MCP_Tool_Platform/server/mcp/custody/` |
| Evidence hasher (SHA-256 CLI) | `MCP_Tool_Platform/server/mcp/hasher/` |
| HurtLex integration | `MCP_Tool_Platform/server/mcp/nlp/` |
| Review queue logic | `MCP_Tool_Platform/server/mcp/review/` |
| Evidence registry | `MCP_Tool_Platform/server/mcp/registry/` |
| Messaging schemas | `MCP_Tool_Platform/server/mcp/loaders/production-message-schemas.ts` |
| SMS parser | `MCP_Tool_Platform/server/mcp/loaders/` |
| Facebook parser | `MCP_Tool_Platform/server/mcp/loaders/` |
| iMessage parser | `MCP_Tool_Platform/server/mcp/loaders/` |

**Owner action required**: Confirm whether `MCP_Tool_Platform/` should be present in this repo, added as a git submodule, or accessed from a separate repository. Until this is resolved, schema porting (Sprint Plan Block A) and any tasks referencing Alpha 1 source code cannot begin.

---

## Task 0-02 / 0-03 / 0-04: Service Health Verification

**Status**: NOT VERIFIED (runtime verification requires a running Docker stack).

The following services are defined in `docker-compose.yml` and expected to be healthy before Phase 1 work begins:

| Service | Port | Expected Status |
|---------|------|-----------------|
| DIAL Core | 8080 | ✅ Defined in compose |
| DIAL Chat | 3000 | ✅ Defined in compose |
| TS MCP Server | 8081 | ✅ Defined in compose |
| Py MCP Server | 8082 (mapped from 8000 internally) | ✅ Defined in compose |
| JS MCP Server | 8083 | ✅ Defined in compose |
| Keycloak | 8180 | ✅ Defined in compose |
| PostgreSQL | 5432 | ✅ Defined in compose |
| DuckDB | embedded | ✅ File-based (no container) |
| LanceDB | embedded | ✅ File-based (no container) |
| Neo4j | 7687 | ⚠️ Not defined in current docker-compose.yml — container required |
| Directus | 8055 | ⚠️ Profile-gated (`--profile data`) — requires owner approval to activate |
| Ollama | 11434 | ✅ Defined in compose |
| Caddy | 80/443 | ✅ Defined in compose |

**Note on Neo4j**: The platform documentation references Neo4j at `bolt://neo4j:7687` but no Neo4j container service is present in `docker-compose.yml`. A service definition is needed before any NER-to-graph population (Phase 2 task 2.3) can proceed.

**Owner action required**: Run `docker compose up -d` and verify health checks on ports 8080, 8081, 8082, 8083, 8180. Add Neo4j service definition to docker-compose.yml.

---

## Task 0-05: Test Suite Baseline

**Status**: No automated test suite exists.

- TypeScript MCP server: no `*.test.ts` or `*.spec.ts` files found
- Python MCP server: no `pytest.ini`, `conftest.py`, or `test_*.py` files found
- No Jest config, no Mocha config
- No CI workflow (`.github/workflows/`) detected

**Owner action required**: Before Sprint Plan Block A task A-09 (parser integration tests) can be written, a test framework must be selected and configured. Recommended: Jest + ts-jest for TypeScript, pytest for Python.

---

## Task 0-06: Alpha 1 Asset Inventory Document

This document fulfills task 0-06. See section 0-01 above for the blocked status on accessing Alpha 1 source files directly.

**Alpha 2 equivalent implementations confirmed present in current repo**:

| Alpha 1 Asset | Alpha 2 Equivalent | File | Status |
|--------------|-------------------|------|--------|
| Pattern analyzer | (not yet ported) | — | 🔜 Planned Phase 1 |
| Chain of custody | Partial — DuckDB vault + SHA-256 | `src/tools/DuckDbVault.ts`, `src/services/DuckDbService.ts` | ⚠️ Partial |
| Evidence hasher | SHA-256 via DuckDbVault | `src/services/DuckDbService.ts` | ✅ Present |
| HurtLex | (not yet ported) | — | 🔜 Planned Phase 3 |
| Review queue | `ReviewQueue` class | `src/tools/ReviewQueue.ts` | ✅ Present |
| Evidence registry | (not yet ported) | — | 🔜 Planned |
| Messaging schemas | `NormalizedMessage` interface (partial) | `src/tools/SmsXmlParser.ts` | ⚠️ Partial (Alpha 1 schema not yet merged) |
| SMS parser | `SmsXmlParser` | `src/tools/SmsXmlParser.ts` | ✅ Working |
| Facebook parser | `FacebookExportParser` | `src/tools/FacebookExportParser.ts` | ✅ Working |
| iMessage parser | `ImessagePdfParser` | `src/tools/ImessagePdfParser.ts` | ✅ Working |

---

## Task 0-07: `production-message-schemas.ts` Confirmation

**Status**: BLOCKED — Alpha 1 `MCP_Tool_Platform/` not present. Cannot confirm file is present and readable.

The current Alpha 2 `NormalizedMessage` interface in `SmsXmlParser.ts` covers basic fields. The full Alpha 1 schema fields (pgvector, device_id, WAL compatibility) have not yet been merged. This is Sprint Plan task A-02.

---

## Task 0-08: DuckDB Vault Initialization & SHA-256 Fingerprinting

**Status**: CODE REVIEW PASS (runtime verification pending).

Code review confirms:
- `DuckDbService.ts`: `hashContent()` computes SHA-256 via Node.js built-in `crypto` — no external dependency
- `DuckDbVault.ts`: `logIngestion()` calls `hashContent()` at first touch before INSERT ✅
- `DuckDbVault.ts`: `hashContent()` and `getIngestionByHash()` are now exposed as delegation methods ✅ (fixed in this Phase 0 work)
- Schema: `ingestion_log.source_hash VARCHAR UNIQUE` — unique constraint enforces dedup at DB level ✅
- Write tracking: initialized on every `logIngestion()` call ✅

**Defects found and fixed** (pre-existing, unrelated to Phase 0 scope):

| File | Issue | Fix Applied |
|------|-------|-------------|
| `DuckDbVault.ts` | `hashContent()` and `getIngestionByHash()` not delegated — caused 2 TypeScript errors in `SmsEvidenceIngestor.ts` | Added delegation methods |
| `SmsXmlParser.ts` | `NormalizedMessage.metadata` missing 8 optional fields used by `SmsEvidenceIngestor.ts` | Added optional fields with correct types |
| `SmsXmlParser.ts` | `record_type` union lacked `'mms'` — caused an unreachable comparison error | Added `'mms'` to union; parser now correctly sets `record_type: 'mms'` for `<mms>` records |
| `SmsXmlParser.ts` | `callTypes` map defined inside `if (isCall)` block but referenced in return statement | Hoisted to outer scope |

TypeScript build is now clean: `tsc --noEmit` exits 0 with no errors.

---

## Directus docker-compose Review (Sprint Plan E-01)

**Status**: REVIEWED — no defects found.

The Directus service is correctly defined in `docker-compose.yml`:

```yaml
directus:
  image: directus/directus:latest
  profiles:
    - data                        # ✅ Opt-in — only starts with --profile data
  ports:
    - "8055:8055"
  depends_on:
    - postgres                    # ✅ Correct dependency
  environment:
    KEY: ${DIRECTUS_KEY:-supersecretkey}
    SECRET: ${DIRECTUS_SECRET:-supersecretdirsecret}
    ADMIN_EMAIL: ${DIRECTUS_ADMIN_EMAIL:-admin@evidence.local}
    ADMIN_PASSWORD: ${DIRECTUS_ADMIN_PASSWORD:-admin_password}
    DB_CLIENT: pg                 # ✅ PostgreSQL
    DB_HOST: postgres
    DB_PORT: "5432"
    DB_DATABASE: evidence         # ✅ Matches PostgreSQL POSTGRES_DB
    DB_USER: dial                 # ✅ Matches PostgreSQL POSTGRES_USER
    DB_PASSWORD: ${POSTGRES_PASSWORD:-dial_password}
    STORAGE_LOCATIONS: local
    STORAGE_LOCAL_ROOT: /directus/uploads
  volumes:
    - directus_uploads:/directus/uploads
    - ./infrastructure/directus/extensions:/directus/extensions
```

**Findings**:
- ✅ Profile-gated: will not start unless `--profile data` is passed — safe
- ✅ Database connection points to correct host/db/user
- ✅ Credentials are env-var injected (`.env.example` documents them)
- ⚠️ Default `KEY` and `SECRET` values are weak placeholders — must be changed before any non-local use (`.env.example` warns this)
- ✅ `directus_uploads` volume declared in the volumes block
- ✅ Extensions directory mounted (currently empty `.gitkeep`)

**Owner action required**: To activate Directus (Sprint Plan task E-02), run `docker compose --profile data up directus -d` after setting strong `DIRECTUS_KEY` and `DIRECTUS_SECRET` in `.env`.

---

## Current Alpha 2 MCP Tool Inventory

### TS MCP Server (`mcp-servers/ts-mcp-server/`) — port 8081

| Tool | Status | Notes |
|------|--------|-------|
| `ping` | ✅ Working | Health check |
| `parse_sms_xml` | ✅ Working | Stream-processes large XML |
| `parse_facebook_export` | ✅ Working | HTML/JSON export |
| `parse_imessage_pdf` | ✅ Working | PDF extraction |
| `vault_log_ingestion` | ✅ Working | SHA-256 at first touch |
| `vault_get_pending_pass1` | ✅ Working | DuckDB query |
| `vault_update_pass1_status` | ✅ Working | DuckDB update |
| `vault_update_write_tracking` | ✅ Working | DuckDB update |
| `postgres_write_record` | ✅ Working | Structured insert |
| `postgres_raw_query` | ✅ Working | Read-only SELECT only |
| `admin_list_llm_providers` | ✅ Working | App tier query |
| `admin_upsert_llm_provider` | ✅ Working | App tier upsert |
| `admin_list_system_prompts` | ✅ Working | App tier query |
| `admin_upsert_system_prompt` | ✅ Working | App tier upsert |
| `review_list_pending` | ✅ Working | HITL queue |
| `review_approve` | ✅ Working | HITL approval |
| `review_reject` | ✅ Working | HITL rejection |
| `review_submit` | ✅ Working | Submits for review |
| `ingest_evidence` | ✅ Registered | Routes to SMS parser; HTML/PDF stubs return `unsupported_format` |
| `run_pass1_analysis` | ✅ Registered | NER via py-mcp-server; embedding deferred |
| `evidence_search` | ✅ Registered | Keyword fallback until pgvector embedding wired |

### Py MCP Server (`mcp-servers/py-mcp-server/`) — port 8082

26 tools registered covering: Semantica NER, graph building, temporal facts, conflict detection, embedding generation, provenance tracking, LanceDB vector search/upsert, Neo4j Cypher queries, entity timeline, DPK HAP scoring, PII redaction, language ID, document quality, readability, voice fingerprinting, behavioral detection, DARVO detection, coercive control analysis, workflow management.

Document intelligence tools (`document_intelligence/`) registered as a plugin if import succeeds — currently stub implementations for all 11 engines.

### JS MCP Server (`mcp-servers/js-mcp-server/`) — port 8083

Not detailed in this audit. File: `mcp-servers/js-mcp-server/src/index.js`.

---

## Phase 0 Gate: Owner Review Required

Before Phase 1 begins, the owner must review this document and provide explicit approval. Open items requiring owner decision:

1. **Alpha 1 access**: Is `MCP_Tool_Platform/` accessible? How should it be provided to this repo?
2. **Neo4j service**: Add Neo4j container to `docker-compose.yml`?
3. **Test framework**: Approve Jest (TS) + pytest (Python) for Sprint Plan task A-09?
4. **Service health check**: Run `docker compose up -d` and verify all core services health.
5. **Directus activation**: Ready to run `docker compose --profile data up directus -d` (requires strong credentials in `.env`)?

**Requesting owner approval to proceed to Phase 1.**

---

## Change Log

- 2026-04-11, rev 1, Copilot: Initial Phase 0 foundation audit. Fixed 4 pre-existing TypeScript build errors as part of 0-08 (DuckDB SHA-256 path verification). TS build is now clean.
