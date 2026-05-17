# INVENTORY REPORT
**Generated**: 2026-05-10  
**Status**: COMPLETE  
**Tool**: INVENTORY_MAPPER

---

## Summary

| | New (Alpha 2) | Old (Alpha 1) |
|---|---|---|
| Root | `/home/user/MCP_PLATFORM` | `/home/user/mcp-tool-platform` |
| Files scanned | 1,501 | 428 |
| Source files (.ts/.py/.js) | 591 | 266 |
| SQL migrations | 9 | 5 |
| Documentation (.md) | 603 | 86 |
| Tests | 0 explicit | 10 (*.test.ts) |
| Excluded | .git, node_modules, __pycache__, .venv, dist, build |

---

## File Type Breakdown

### New (Alpha 2)
| Type | Count |
|---|---|
| .md (docs) | 603 |
| .py | 565 |
| .tsx | 63 |
| .ts | 22 |
| .json | 33 |
| .sql | 9 |
| .yml/.yaml | 17 |
| .js | 4 |
| .sh | 4 |
| .ps1 | 6 |

### Old (Alpha 1)
| Type | Count |
|---|---|
| .ts | 159 |
| .md | 86 |
| .tsx | 77 |
| .py | 20 |
| .json | 24 |
| .sql | 5 |
| .js | 10 |

---

## New Codebase — Priority Targets

### Entry Points
| File | Role |
|---|---|
| `mcp-servers/ts-mcp-server/src/index.ts` | TS MCP server entry, tool registration |
| `mcp-servers/py-mcp-server/src/server.py` | Py MCP server entry |
| `mcp-servers/js-mcp-server/src/index.js` | JS MCP server entry |
| `docker-compose.yml` | Full stack definition (has DIAL — see handoff) |
| `.env.example` | All env vars documented |
| `GROUND_TRUTH.md` | Authoritative platform state — read first |
| `DECISION_REGISTER.md` | All 33 ADRs |

### SQL Migrations
| File | Purpose |
|---|---|
| `migrations/001_pgcrypto_hash_verification.sql` | pgcrypto extension + hash functions |
| `migrations/002_eastern_time_functions.sql` | Timezone helpers |
| `migrations/003_deleted_message_storage.sql` | Soft-delete storage |
| `migrations/004_chain_of_custody.sql` | CoC table + audit trail |
| `migrations/005_message_chunks.sql` | Chunked message storage for embeddings |
| `infrastructure/init/postgres/00–03.sql` | Bootstrap + extensions + identification tools |

### TS MCP Server Tools (`mcp-servers/ts-mcp-server/src/tools/`)
| File | Size | State |
|---|---|---|
| `SmsXmlParser.ts` | — | ✅ Working |
| `SmsEvidenceIngestor.ts` | — | ✅ Working |
| `EvidenceIngestor.ts` | — | ✅ Router (Facebook/iMessage return "unsupported") |
| `FacebookExportParser.ts` | — | ⚠️ STUB — port priority #1 |
| `ImessagePdfParser.ts` | — | ⚠️ STUB — port priority #2 |
| `Pass1Runner.ts` | 13KB | ✅ Exists — verify completeness |
| `MessageChunker.ts` | 5.5KB | ✅ Working |
| `DuckDbVault.ts` | 2.4KB | ✅ Working |
| `PostgresWriter.ts` | 6.8KB | ✅ Working |
| `ReviewQueue.ts` | 3.3KB | ✅ Working |
| `SbvClient.ts` | 6.6KB | ✅ Working |
| `SbvIngestor.ts` | 15KB | ✅ Working (largest tool) |
| `AdminTools.ts` | 3.8KB | ✅ Working |
| `constants.ts` | 449B | ✅ Working |

### Py MCP Server (`mcp-servers/py-mcp-server/src/`)
| File | State |
|---|---|
| `server.py` | ✅ Entry point |
| `tools/evidence_signing.py` | ✅ SHA-256 signing |
| `tools/hash_verification.py` | ✅ Hash verification |
| `tools/audit_hooks.py` | ✅ Audit trail |
| `tools/dpk_tools.py` | ✅ Data Prep Kit tools |
| `tools/sqlite_wal_parser.py` | ✅ SQLite WAL parsing |
| `tools/user_detection.py` | ✅ User detection |
| `tools/voice_tools.py` | ✅ Voice transcription tools |
| `tools/workflow_tools.py` | ✅ Workflow tooling |
| `document_intelligence/router.py` | ✅ EngineRouter built |
| `document_intelligence/engine_registry.py` | ✅ Registry built |
| `document_intelligence/engines/pandoc_engine.py` | ⚠️ Stub — activate first (local, free) |
| `document_intelligence/engines/tesseract_engine.py` | ⚠️ Stub — activate second (local, free) |
| `document_intelligence/engines/*` | ⚠️ 9 other stubs — per ADR-024 activation order |

---

## Storage & Retrieval Architecture

The full data infrastructure plan. **No port should bypass this layout.** Semantica is the only sanctioned path to Neo4j and LanceDB — direct clients are forbidden.

| Tier | Component | Role | Accessed Via |
|---|---|---|---|
| T1 | **DuckDB** | WORM forensic vault — Pass 1 immutable storage, SHA-256 sealed | `ts-mcp-server` `DuckDbVault.ts` |
| T2 | **LanceDB** | Vector store — 768-dim embeddings, semantic search | **Semantica only** (`lancedb_vector_search`, `lancedb_upsert`) |
| T3 | **Neo4j** | Knowledge graph — entities, relations, temporal facts | **Semantica only** (`neo4j_cypher_query`, `neo4j_get_entity_timeline`) |
| T4 | **PostgreSQL** | Operational/relational store — chunks, queues, audit | `ts-mcp-server` `PostgresWriter.ts`, migrations 001–005 |
| NLP | **Semantica** ⭐ | NER + relation extraction + temporal facts + conflict detection + embeddings — **replaces Graphiti**, non-negotiable | `py-mcp-server` (FastMCP, 11 tools) — upstream: https://github.com/Hawksight-AI/semantica |
| API | **WunderGraph Cosmo** (:4000) | GraphQL federation — unified retrieval layer over all tiers | `infrastructure/` (docker-compose) |

### Why Semantica is VIP
- Pass 1 (blind, 24h window, WORM) and Pass 2 (longitudinal, contradiction detection) both flow through Semantica
- It is the only producer of embeddings and graph writes
- Pass1Runner (TS) calls Semantica tools over MCP — do not duplicate its logic in TS
- Treat the Semantica tool interfaces as authoritative; do not rewrite or stub them

### Old → New Storage Mapping
| Alpha 1 | Alpha 2 |
|---|---|
| `graphiti-client.ts` | Semantica (`neo4j_*` + `lancedb_*` tools) |
| `chroma-client.ts`, `chroma/*` | Semantica `lancedb_*` tools |
| `pgvector-client.ts` | LanceDB via Semantica (pgvector retired) |
| `redis-queue.ts` | Dragonfly |
| `db.mysql.ts` | PostgreSQL only |
| Any direct Neo4j driver | Forbidden — go through Semantica |

---

## Old Codebase — Port Candidates

### Highest Priority (directly needed for INGEST milestone)
| Old File | Target in New | Notes |
|---|---|---|
| `server/mcp/loaders/facebook-parser.ts` | `ts-mcp-server/src/tools/FacebookExportParser.ts` | Port priority #1 |
| `server/mcp/loaders/pdf-imessage-parser.ts` | `ts-mcp-server/src/tools/ImessagePdfParser.ts` | Port priority #2 |
| `drizzle/production-message-schemas.ts` | New migration `006_messaging_schemas.sql` | Port fields, not Drizzle wrapper |
| `server/mcp/forensics/chain-custody.ts` | Verify against `migrations/004` + DuckDbVault | Has tests — port them too |
| `server/mcp/plugins/evidence-hasher.ts` | `ts-mcp-server/src/tools/` | SHA-256 at first touch (ADR-011) |

### High Priority (NLP + analysis — needed for SEARCH/OUTPUT milestones)
| Old File | Target in New | Notes |
|---|---|---|
| `server/mcp/forensics/hurtlex-stream.ts` | `py-mcp-server/src/tools/` | HurtLex NLP — MCL 722.23 DV factor |
| `server/mcp/forensics/pattern-analyzer.ts` | `py-mcp-server/src/tools/` | DARVO/coercive control detection |
| `server/mcp/forensics/timeline-generator.ts` | `py-mcp-server/src/tools/` | Court-ready timeline output |
| `server/mcp/analysis/classifier.ts` | `py-mcp-server/src/tools/` | Multi-pass classifier |
| `server/mcp/analysis/nlp-classifier.ts` | `py-mcp-server/src/tools/` | NLP classification |

### Document Intelligence Engine Sources
| Old File | Target in New | Notes |
|---|---|---|
| `server/mcp/plugins/format-converter.ts` (725 LOC) | `engines/pandoc_engine.py` | Activate Pandoc engine |
| `server/mcp/plugins/ocr.ts` (333 LOC) | `engines/tesseract_engine.py` | Activate Tesseract engine |

### Supporting / Lower Priority
| Old File | Notes |
|---|---|
| `server/mcp/loaders/xml-sms-parser.ts` | Reference for SmsXmlParser (already ported) |
| `server/mcp/loaders/embedding-pipeline.ts` | Reference for LanceDB write path |
| `server/mcp/loaders/real-embedding-service.ts` | Reference for embedding service |
| `server/mcp/prompts/prompt-manager.ts` | Prompt management patterns |
| `server/mcp/forensics/forensics-router.ts` | Forensics routing logic |

### DO NOT PORT
| Old File | Reason |
|---|---|
| `server/mcp/orchestration/langchain-memory.ts` | Replaced by Conductor OSS (ADR-033) |
| `server/mcp/orchestration/langgraph*.ts` | Same — deprecated |
| `server/mcp/plugins/n8n.ts` | n8n deprecated per ADR-033 |
| `server/mcp/storage/chroma-client.ts` | Replaced by LanceDB |
| `server/mcp/storage/graphiti-client.ts` | Replaced by **Semantica** (wraps Neo4j + LanceDB) — never call Neo4j directly |
| `server/core/db.mysql.ts` | Wrong DB — PostgreSQL only |
| `server/mcp/queue/redis-queue.ts` | Replaced by Dragonfly |
| `server/mcp/chroma/*.ts` | Replaced by LanceDB |

---

## Manifest Files

| File | Contents | Format |
|---|---|---|
| `manifest_new.tsv` | All 1,501 files in Alpha 2 | md5hash \t size_bytes \t ext \t path |
| `manifest_old.tsv` | All 428 files in Alpha 1 | md5hash \t size_bytes \t ext \t path |
| `port_candidates.txt` | Old files with no filename match in new | plaintext |
| `filetype_breakdown.txt` | File type counts + directory sizes | plaintext |

---

## Unresolved
None.

---

## Notes for Context Summarizer
- Transcripts path: NONE
- Alpha 2 has 603 .md docs but only 22 .ts source files — heavily documented, lightly coded
- Alpha 1 has 159 .ts files to Alpha 2's 22 — most of the real source logic is still in Alpha 1
- All Alpha 1 tests (*.test.ts) are in `server/mcp/forensics/` — port alongside source
- Alpha 1 uses Drizzle ORM — extract column definitions only, never port the Drizzle schema wrapper
- Hash manifests enable future agents to skip unchanged files on re-scan
