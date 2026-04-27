# Alpha 1 Inventory — Port Reference
> **Sources**: `MCP_Tool_Platform_Repo-2.zip` (197 files) + `github.com/Cursedpotential/mcp-tool-platform` (428 files — canonical)
> **Generated**: 2026-04-27 | Cross-referenced against Alpha 2 `GROUND_TRUTH.md`
> **Port plan**: `docs/wiki/alpha1-port-plan.md`

---

## What Alpha 1 Is

Alpha 1 is a **production forensic evidence ingestion and NLP analysis platform** — not a prototype. It was running on a 3-VPS Tailscale mesh (Salem Trinity: Nexus + Forge + Platform nodes) with MySQL app layer + PostgreSQL evidence layer.

Key numbers:
- **428 files** across 60+ directories
- **18-table Drizzle ORM schema** (dual-layer: MySQL app + PostgreSQL evidence)
- **80+ registered MCP tools** via a working plugin registry
- **Full tRPC API layer** (ingestion, HITL, patterns, pattern-approval, agents, graphiti, CopilotKit)
- **14-page React 19 frontend** (4 complete, rest partial)
- **Cloudflare Workers** deployed at edge (evidence hasher, R2 storage, auth, rate limiter, cache, webhook)
- **GCP Cloud Run** Graphiti/Neo4j REST API

---

## File Inventory by Domain

### Parsers / Loaders (`server/mcp/loaders/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `base-loader.ts` | `BaseDocumentLoader` abstract class. `LoadedDocument` + `DocumentMetadata` types. 5 chunking strategies: `fixed_size`, `sliding_window`, `semantic`, `conversation_turn`, `paragraph`. Thread grouping logic. | Interface contracts should inform Alpha 2 `EvidenceBatch` schema |
| `sms-loader.ts` | `SMSDocumentLoader` — JSON/CSV/XML/TXT multi-format. Thread grouping by participant. | PORTED — SMS XML parser working in Alpha 2 |
| `facebook-parser.ts` | `FacebookHTMLParser` — **streaming HTML** (NOT JSON). Dual-structure: `div.message` + `div._a6-g` card layout. Fuzzy date parsing. Direction detection. Multi-GB capable. | Alpha 2 `FacebookExportParser.ts` handles both structures but lacks streaming for large files |
| `pdf-imessage-parser.ts` | `PDFImessageParser` — **Python bridge** via `pdf_extractor.py` (pdfplumber). Two message formats. Multi-line continuation. | Alpha 2 `ImessagePdfParser.ts` uses `pdf-parse` (Node.js only) — no Python bridge |
| `xml-sms-parser.ts` | `XMLSmsParser` — streaming, multi-GB. SAX-style. | PORTED |
| `embedding-pipeline.ts` | `EmbeddingVector` + `EmbeddingMetadata` types. `SemanticSearchQuery` + `SearchFilters`. Retry logic (3 attempts). Batch processing. OpenAI-compatible API. Handles both response formats. | NOT PORTED — needed for LanceDB write path |
| `real-embedding-service.ts` | `RealEmbeddingService` — production embedding service wrapping embedding-pipeline. | NOT PORTED |
| `document-hierarchy.ts` | Document tree / hierarchy builder | NOT PORTED |
| `lexicon-importer.ts` | Generic GitHub/URL/local lexicon fetcher. `LEXICON_REGISTRY` extensible config. Conflict resolution, language filtering, category mapping. Currently configured for HurtLex. | NOT PORTED |
| `unstructured-loader.ts` | Unstructured.io loader integration | NOT PORTED |
| `pgvector-setup.sql` | pgvector extension setup. `match_embeddings()` function with metadata filters. HNSW index. | NOT PORTED — relevant if Alpha 2 adds pgvector |

### Forensics (`server/mcp/forensics/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `chain-custody.ts` | SHA-256 JSONL chain of custody. File-based. Hash at every stage. | Alpha 2 has `evidence_signing.py` (Ed25519 — more advanced). Do not port. |
| `pattern-analyzer.ts` | **18 analysis modules** (gaslighting, blame-shifting, threats, isolation, financial control, emotional blackmail, love bombing, DARVO, minimization, etc.). 256+ built-in regex patterns. `LinguisticAnalysis` (pronoun ratios, hedge/certainty, overelaboration). MCL 722.23 factor scoring per match. `PatternMatch`, `AnalysisResult`, `Contradiction`, `TimelineEvent` types. | NOT PORTED — **TIER 1 priority** |
| `pattern-analyzer.test.ts` | Test suite for pattern-analyzer | Port with implementation |
| `timeline-generator.ts` | Timestamp extraction (10 regex pattern types). **Lenore Walker cycle-of-abuse detection** (tension/incident/reconciliation/calm phases with weighted regex indicators). `EscalationData` (weekly/monthly severity trends). Markdown timeline report generation. Uses `compromise` NLP + `date-fns`. | NOT PORTED — **TIER 1 priority** |
| `timeline-generator.test.ts` | Test suite | Port with implementation |
| `hurtlex-stream.ts` | **HurtLex lexicon** streaming from GitHub raw TSV. 17 categories (PS, RCI, PA, DDF, DDP, DMC, IS, OR, AN, ASM, ASF, PR, OM, QAS, CDS, RE, SVP). 1-hour in-memory cache (no DB). `fetchTerms()`, `searchTerms()`, `matchText()`, `getCategoryCounts()`. | NOT PORTED — **TIER 1 priority** |
| `hurtlex-fetcher.ts` | HurtLex fetch utility (used by hurtlex-stream) | NOT PORTED |
| `behavior-service.ts` | In-memory regex behavior detection fallback. Simplified version of pattern-analyzer. | Superseded by pattern-analyzer port |
| `identity-service.ts` | `IdentityService` — deterministic conversation ID (SHA-256 of sorted participants). Get-or-create `messagingConversations` in PostgreSQL. `hashContent()` util. | Alpha 2 has equivalent logic in ts-mcp-server — verify parity |
| `forensics-router.ts` | tRPC forensics router — wires all forensics services together | Architecture change — Alpha 2 is MCP-native, not tRPC |

### Analysis (`server/mcp/analysis/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `multi-pass-classifier.ts` | **6-pass NLP classifier**: Pass 0 (priority screener) → Pass 1 (spaCy structure) → Pass 2 (VADER sentiment) → Pass 3 (pattern analyzer) → Pass 4 (TextBlob) → Pass 5 (sentence-transformers semantic). Output: `MultiPassClassification` with speaker detection, sentiment consensus, MCL factors, severity 1-10, confidence 0-1. | NOT PORTED — **TIER 1 priority** |
| `multi-pass-classifier.test.ts` | Test suite | Port with implementation |
| `nlp-classifier.ts` | Individual NLP classifier (used by multi-pass). spaCy + NLTK + TextBlob integration. | NOT PORTED |
| `conversation-segmentation.ts` | Cluster ID assignment: `PLAT_YYMM_TOPIC_iii` format. 8 platform codes. 30+ topic codes (KAILAH, VISITS, CALLS, SCHOOL, MONEY, HEALTH, SUBST, INFID, THREAT, etc.). spaCy keyword extraction. | NOT PORTED — **TIER 1 priority** |
| `classifier.ts` | Base classifier | NOT PORTED |
| `priority-screener.ts` | **Pass 0** — immediate flags for child name variants (Kailah/Kyla/Kaila/Kailuh), custody interference, call blocking, parental alienation. Hardcoded patterns — port verbatim. | NOT PORTED (part of multi-pass) |

### Plugins (`server/mcp/plugins/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `evidence-hasher.ts` | SHA-256 hasher plugin (file-based) | Alpha 2 `hash_verification.py` is more complete. Do not port. |
| `evidence-linker.ts` | Cross-evidence analysis. Links evidence to Neo4j entities. Evidence clustering by topic. Cross-source correlation. Timeline reconstruction. Uses PostgreSQL + Neo4j + pgvector. | NOT PORTED — Semantica domain (graph tools). Flag if Semantica graph tools are stubs. |
| `graph-analytics.ts` | Neo4j Graph Data Science — community detection (Louvain, Label Propagation, Connected Components), centrality (PageRank, Betweenness, Degree), entity resolution + deduplication. | NOT PORTED — Semantica domain |
| `agent-memory.ts` | **Agent working memory in Graphiti/Neo4j**. `AgentContext`, `AgentDecision`, `AgentMessage`, `SessionHistory` types. Agent-to-agent coordination. Cross-session memory persistence. graphiti-client TODO'd out. | DEFERRED (ROOF) — future agent/model memory layer |
| `pattern-persistence.ts` | Saves detected patterns to PostgreSQL with approval workflow. Wires to `create_pattern_persistence_tables.sql`. | NOT PORTED |
| `registry.ts` | `PluginRegistry` — tool registration, tag indexing, semantic search by query/topK/category/tags. `PluginManifest` bulk registration. | NOT PORTED — **TIER 3 priority** |
| `bert-sentiment.ts` | BERT-based sentiment (via Python bridge) | NOT PORTED |
| `nlp.ts` | NLP plugin wrapper | NOT PORTED |
| `ocr.ts` | OCR plugin | NOT PORTED — Alpha 2 has 11 document intelligence engines |
| `vector-db.ts` | Vector DB plugin | NOT PORTED |
| `xml-streaming-parser.ts` | XML streaming plugin | PORTED |
| `schema-resolver.ts` | Schema resolution | NOT PORTED |
| `retrieval.ts` | Retrieval plugin | NOT PORTED |
| `html-parser.ts` | HTML parser plugin | Covered by Facebook parser |
| `markdown-parser.ts` | Markdown parser | NOT PORTED |
| `xml-parser.ts` | XML parser | PORTED |
| `timeline-parser.ts` | Timeline parsing plugin | NOT PORTED |
| `spatial-analytics.ts` | Geospatial pattern detection — clusters, routes, stops, meeting points. Geofence violations. | NOT PORTED — future feature |

### Schemas (`server/mcp/schemas/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `facebook_messages.json` | Facebook HTML export field schema — `div.message`, `.sender-name`, `.message-text`, `.timestamp` | Reference — Alpha 2 parser covers this |
| `snapchat_messages.json` | **Snapchat HTML export schema** — container, sender, text, timestamp structure | NOT IN ALPHA 2 — needed for Snapchat parser (TIER 2) |

### Python Tools (`server/python-tools/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `pdf_extractor.py` | pdfplumber-based PDF extractor. Used by `pdf-imessage-parser.ts` as Python bridge. Two message formats. Multi-line continuation. | NOT PORTED — needed for iMessage Python bridge (TIER 0) |
| `nlp_runner.py` | Python NLP runner — spaCy, NLTK, TextBlob, sentence-transformers. Used by multi-pass classifier. | NOT PORTED — needed for multi-pass (TIER 1) |
| `get_embedding.py` | Embedding generation via OpenAI-compatible API | NOT PORTED |
| `topic_detector.py` | Topic detection | NOT PORTED |
| `unstructured_parser.py` | Unstructured.io parser | Alpha 2 has `unstructured_engine.py` |

### Drizzle Schema (`drizzle/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `production-message-schemas.ts` | **Canonical production schema** — `messaging_documents`, `messaging_conversations`, `messaging_messages`, `messaging_attachments`, `messaging_behaviors`, `messaging_evidence_items`, `messaging_factor_citations`, MCL factor + behavior category reference tables. Key fields: `mcl_factors[]`, `exhibit_number`, `relevance_score`, `timestamp_precision`, `direction` enum, `body_lower`, `content_hash`, `previous_message_id`/`next_message_id`. | ADR-028 — Alpha 2 migrations merge this as source of truth. Diff against migrations 001-005 before any schema work. |
| `schema.ts` | MySQL app layer tables (users, sessions, cases, review queue, etc.) | Architecture change — Alpha 2 uses PostgreSQL + Directus |
| `message-schemas.ts` | Earlier iteration of message schemas | Superseded by `production-message-schemas.ts` |

### Database Migrations (`server/database/migrations/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `create_pattern_persistence_tables.sql` | **7 tables + 2 views + audit functions**: `detected_patterns`, `pattern_occurrences`, `evidence_clusters`, `spatial_patterns`, `geofence_violations` (auto-approved), `inferred_relationships`, `pattern_approval_log`. Views: `pending_patterns`, `approved_patterns`. Status flow: `pending → approved/rejected`. | NOT PORTED — needed for pattern approval HITL workflow |

### API Routers (`server/api/routers/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `hitl.ts` | tRPC HITL router — `createRequest`, `getRequest`, `listPending`, `approve` (auto-executes), `reject`, `rollback`. Action types: write/delete/move/merge/execute. | Architecture change — Alpha 2 HITL goes through CopilotKit + ReviewQueue. Approval/reject logic is reference. |
| `ingestion.ts` | tRPC ingestion router — full ingest pipeline wired: XML → identity-service → behavior-service → PostgreSQL batch + ChromaDB + Graphiti. Hash on entry. UUIDv7 IDs. `BATCH_SIZE=50`. | Architecture change — MCP-native in Alpha 2. Pipeline logic is reference for `EvidenceIngestor.ts`. |
| `pattern-approval.ts` | tRPC pattern approval router — `getPendingPatterns`, `approvePattern`, `rejectPattern` against `pending_patterns` view. Paginated. Category filter. | Architecture change — MCP-native in Alpha 2. Logic informs Alpha 2 review queue extension. |
| `agents.ts` | tRPC agents router | Architecture change |
| `graphiti.ts` | tRPC Graphiti router | Architecture change — Semantica domain |

### CopilotKit (`server/api/copilotkit/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `index.ts` | `CopilotRuntime` wired to `PluginRegistry` + `TaskExecutor`. Dynamically registers all MCP tools as CopilotKit actions. `OpenAIAdapter`. | **Direct reference for OQ-C5** — this is how Conductor HUMAN task ↔ ReviewQueue ↔ CopilotKit bridge should work in Alpha 2. Pattern is proven. |

### Utility Scripts (`utilities/scripts/`)
| File | What it does | Alpha 2 status |
|---|---|---|
| `chatgpt_parser.py` | **Full ChatGPT JSON export parser**. `ConversationTurn`, `Entity`, `Artifact` dataclasses. spaCy NER. Code block extraction with language detection. SHA-256 per message. JSONL output. | NOT PORTED — **TIER 2 new source** |
| `conversation_splitter.py` | Splits ChatGPT JSON exports by N conversations per chunk. Handles both `{conversations:[]}` and bare array. Windows UTF-8 safe. | NOT PORTED — TIER 4 utility |
| `find_duplicates.py` | SHA-256-based duplicate file finder across directory tree | NOT PORTED — TIER 4 utility |
| `batch_json_splitter.py` | Batch-processes directory of JSON files with configurable chunk size | NOT PORTED — TIER 4 utility |
| `output_schemas.py` | Validates JSONL output against `ConversationTurn`/`Entity`/`Artifact` schemas | NOT PORTED — TIER 4 utility |
| `analyze_triggers.py` | Skill trigger anti-pattern analyzer | SKIP — not relevant to forensics pipeline |
| `clean_markdown_converter.py` | Markdown conversion utility | NOT YET READ |
| `conversation_to_docx.py` | Conversation → DOCX export | NOT YET READ |
| `docx_to_pdf.py` | DOCX → PDF conversion | NOT YET READ |
| `compare_nltk_vs_agent.py` | NLTK vs agent output comparison | NOT YET READ |
| `chunk_file_tool.py` | File chunking utility | NOT YET READ |

### Deployment (`deploy/`)
| Directory | What it does | Alpha 2 status |
|---|---|---|
| `deploy/cloudflare/` | **6 Cloudflare Workers**: `evidence-hasher.js` (edge hash + KV chain storage), `r2-storage.js` (file upload/download/presign), `auth-proxy.js`, `rate-limiter.js`, `cache-api.js`, `webhook-receiver.js`. `wrangler.toml` present. | NOT PORTED — **TIER 3**. Copy with wrangler.toml, update env vars. |
| `deploy/gcp/graphiti/` | FastAPI + Graphiti-core on Cloud Run. Pydantic models. Neo4j Aura backend. LiteLLM-compatible. | DEFERRED (ROOF) — future agent/model memory layer. Not a forensic graph substitute. |
| `deploy/salem-trinity/` | 3-VPS Tailscale mesh deployment configs (Nexus/Forge/Platform) | Architecture change — not porting VPS topology |

### Docs (`docs/`, root)
| File | What it does | Alpha 2 relevance |
|---|---|---|
| `WHAT_IS_THIS_PROJECT.md` | One-paragraph mission statement | Still accurate at high level — reference |
| `PROJECT_STATUS.md` | Alpha 1 project status at time of repo | Historical reference |
| `BACKEND_ARCHITECTURE.md` | Dual-concern architecture explanation (app vs. evidence layer) | Useful historical context |
| `BACKEND_ARCHITECTURE.md` | Dual-concern architecture explanation | Reference |
| `STORAGE_ARCHITECTURE.md` | Storage layer decisions | Reference |
| `GAP_ANALYSIS_PRIORITIES.md` | Gap analysis at Alpha 1 end state | Superseded by Alpha 2 GROUND_TRUTH.md |
| `docs/PROJECT_INTEL_SSOT.md` | Canonical description of the case/platform purpose | Reference |
| `docs/analysis/GAP_ANALYSIS.md` | Historical gap analysis | Reference |
| `docs/MCP_TOOL_CATALOG.md` | Tool definitions — informs Alpha 2 tool naming | Reference |
| `FRAMEWORK_DECISION_MATRIX.md` | Framework evaluation decisions | Reference |
| `FRAMEWORK_LEVERAGE_OPPORTUNITIES.md` | Framework leverage opportunities | Reference |
| `utilities/Legal_Document_Parsing_Best_Practices.md` | Legal doc parsing guidance | Reference — relevant to report generation |

---

## Items Not Yet Read

These files exist in the repo but were not read during inventory. Read before porting:

| File | Why it matters |
|---|---|
| `utilities/scripts/clean_markdown_converter.py` | May be relevant to report generation |
| `utilities/scripts/conversation_to_docx.py` | May be relevant to export pipeline |
| `utilities/scripts/docx_to_pdf.py` | May be relevant to export pipeline |
| `utilities/scripts/compare_nltk_vs_agent.py` | May inform classifier benchmarking |
| `utilities/scripts/chunk_file_tool.py` | May inform chunking strategy |
| `server/mcp/plugins-pending/` | Entire directory not read — unknown contents |
| `server/mcp/store/` | Storage layer — unknown contents |
| `server/mcp/orchestration/` | Alpha 1 orchestration — may contain workflow patterns |
| `server/mcp/workers/executor.ts` | Task executor — relevant to OQ-C5 CopilotKit bridge |
| `server/mcp/hitl/approval.ts` | HITL approval implementation — relevant to Alpha 2 ReviewQueue |
| `server/mcp/storage/graphiti-client.ts` | Graphiti client — needed before any graph tool work |
| `server/core/` (24 files) | Core layer — trpc setup, db connections, auth |
| `shared/types.ts`, `shared/workflow-types.ts` | Canonical type contracts — read before writing any port |
| `drizzle/production-message-schemas.ts` | **MUST READ before T0-2** — full field list needed for migration diff |

---

## Alpha 1 → Alpha 2 Component Map (Summary)

| Alpha 1 | Alpha 2 | Action |
|---|---|---|
| `FacebookHTMLParser` (streaming) | `FacebookExportParser.ts` (functional, no streaming) | Add streaming path for large files |
| `PDFImessageParser` (Python bridge) | `ImessagePdfParser.ts` (Node pdf-parse only) | Add Python bridge / wire `pdf_extractor.py` |
| `XMLSmsParser` | SMS XML parser | DONE |
| `chain-custody.ts` (SHA-256) | `evidence_signing.py` (Ed25519) | Alpha 2 wins — do not port |
| `evidence-hasher.ts` | `hash_verification.py` | Alpha 2 wins — do not port |
| `PatternAnalyzer` (18 modules, 256+ patterns) | Nothing | PORT — Tier 1 |
| `HurtLexStream` (17 categories, TTL cache) | Nothing | PORT — Tier 1 |
| `TimelineGenerator` (Walker cycle detection) | Nothing | PORT — Tier 1 |
| `MultiPassClassifier` (6 passes) | Nothing | PORT — Tier 1 |
| `ConversationSegmentation` (cluster IDs) | Nothing | PORT — Tier 1 |
| `IdentityService` (deterministic conv ID) | Verify equivalent exists | VERIFY |
| `EmbeddingPipeline` / `RealEmbeddingService` | LanceDB write path (stub) | PORT — Tier 3 |
| `PluginRegistry` | Nothing | PORT — Tier 3 |
| `LexiconImporter` | Nothing | PORT — Tier 3 |
| `create_pattern_persistence_tables.sql` | Nothing | PORT — needed for HITL pattern approval |
| `pattern-approval` router logic | ReviewQueue extension | Reference for Alpha 2 MCP tool |
| `CopilotKit/index.ts` (registry→actions bridge) | OQ-C5 unresolved | **Direct reference** — pattern proven |
| `agent-memory.ts` (AgentContext/Decision/Message) | Nothing | DEFERRED — Graphiti agent memory (ROOF) |
| `deploy/gcp/graphiti/` | Nothing | DEFERRED — agent memory (ROOF) |
| `deploy/cloudflare/` (6 workers) | Nothing | PORT — Tier 3 |
| `chatgpt_parser.py` | Nothing | PORT — Tier 2 new source |
| Snapchat schema | Nothing | PORT — Tier 2 new source (build new parser) |
| `production-message-schemas.ts` | Alpha 2 migrations (partial) | DIFF + fill gaps — Tier 0 |
| Utility scripts (splitter, dedup, batch) | Nothing | PORT — Tier 4 |
| Alpha 1 React client | CopilotKit + NLUX | Architecture change — do not port |
| Alpha 1 tRPC routers | MCP tool surface | Architecture change — logic is reference only |
| Alpha 1 MySQL app schema | PostgreSQL + Directus | Architecture change — do not port |
| Alpha 1 Salem Trinity VPS topology | Alpha 2 deployment | Architecture change — do not port |

---

*Read the repo before theorizing. This inventory is based on direct file reads of both Alpha 1 sources (zip + GitHub repo).*
