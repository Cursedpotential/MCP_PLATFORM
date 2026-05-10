# Alpha 1 → Alpha 2 Port Plan
> Generated: 2026-04-21 | Source A: `MCP_Tool_Platform_Repo-2.zip` (197 files) | Source B: `github.com/Cursedpotential/mcp-tool-platform` (414 files)
> Cross-referenced against: `github.com/Cursedpotential/MCP_PLATFORM` (Alpha 2 GROUND_TRUTH.md)

---

## What Alpha 1 Actually Is

Alpha 1 is **not a prototype**. It is a 65%-complete forensic evidence ingestion and NLP analysis platform with:

- **13,265 lines** across 26 plugin modules
- **80+ registered MCP tools** in a fully compliant MCP gateway
- **18-table Drizzle ORM schema** (MySQL app layer + PostgreSQL evidence layer)
- **Full forensic chain of custody** with SHA-256 hashing at every stage
- **Multi-pass NLP classifier** (spaCy + NLTK + TextBlob + sentence-transformers + pattern-analyzer)
- **HurtLex hate speech lexicon** integrated (streaming, in-memory, no DB required)
- **Full behavioral pattern library** — 256+ patterns across 18 categories with MCL 722.23 factor mapping
- **Timeline generator** with Lenore Walker cycle-of-abuse detection
- **Cloudflare Workers** for edge-deployed evidence hasher + R2 file storage
- **GCP Cloud Run** Graphiti/Neo4j REST API
- **Multi-VPS deployment** (Nexus + Forge architecture, Tailscale mesh)
- **React 19 frontend** with 14 pages (4 complete, rest partial or stubbed)
- **n8n workflows** for Docker service control
- **Full tRPC API layer** including forensics router, patterns router, HITL router, ingestion router

The zip (197 files) is a **subset** of the repo (414 files). The repo has everything the zip has plus: the full `client/` React app, all deployment configs, all docs/analysis, the Drizzle migrations, Cloudflare Workers, GCP deployment, n8n workflows, and architecture docs.

---

## Alpha 2 Current State (from GROUND_TRUTH.md)

| Component | Alpha 2 Status |
|---|---|
| SMS XML parser | PORTED — working |
| Facebook parser | EXISTS — functional HTML parser using cheerio, dual-structure support |
| iMessage PDF parser | EXISTS — uses pdf-parse (Node.js only, no Python bridge) |
| Chain of custody (TS) | EXISTS in `evidence_signing.py` (Ed25519, more advanced than Alpha 1) |
| Hash verification | EXISTS in `hash_verification.py` |
| Pass1Runner | EXISTS — verify completeness |
| DuckDB vault | EXISTS |
| PostgreSQL writer | EXISTS |
| Review queue | EXISTS — HITL approve/reject |
| Document intelligence engines (11) | ALL STUBS |
| Pattern analyzer | NOT PORTED |
| HurtLex | NOT PORTED |
| Timeline generator | NOT PORTED |
| Multi-pass classifier | NOT PORTED |
| Embedding pipeline | NOT PORTED |
| Graphiti/Neo4j memory | OWNED BY SEMANTICA — not a port item (ADR-007) |
| Plugin registry | NOT PORTED |
| Cloudflare Workers | NOT PORTED |
| R2 storage | NOT PORTED |
| Conversation segmentation | NOT PORTED |
| Priority screener | NOT PORTED |
| ChatGPT export parser | NOT PORTED |
| Snapchat parser | NOT PORTED |
| Utility scripts | NOT PORTED |

---

## Critical Corrections to Prior Session Notes

The context summary stated `FacebookExportParser.ts` and `ImessagePdfParser.ts` were "STUB ONLY." **This is incorrect.** Both are functional implementations:

- **`FacebookExportParser.ts`** — Fully functional HTML parser using cheerio. Handles two Facebook export structures (`div.message` + `div._a6-g` cards). Fuzzy date parsing. Direction detection. Message type classification. Not a stub.
- **`ImessagePdfParser.ts`** — Functional PDF parser using `pdf-parse` (Node.js). Handles two message formats. Multi-line continuation. Not a stub.

**What is actually missing vs Alpha 1:**
- Alpha 2's `FacebookExportParser` does NOT have the streaming capability for multi-gigabyte files that Alpha 1's parser has. Alpha 1 uses a streaming HTML approach for large files.
- Alpha 2's `ImessagePdfParser` does NOT have the Python bridge (`pdfplumber`) that Alpha 1 uses. Alpha 1's bridge is more reliable for complex PDF layouts.
- Neither parser is wired into `EvidenceIngestor.ts` — it explicitly returns `unsupported_format` for `.html` and `.pdf`. That's the actual gap.

---

## Port Priority Tiers

### TIER 0 — Unblock Ingest (Do First — Outcome 1 Dependency)

These are blocking the entire pipeline. Nothing runs without them.

#### T0-1: Wire `EvidenceIngestor.ts` to call `FacebookExportParser` and `ImessagePdfParser`
- **Alpha 1 source:** `server/mcp/forensics/forensics-router.ts` — the call pattern
- **Alpha 2 target:** `ts-mcp-server/src/tools/EvidenceIngestor.ts`
- **What to do:** Remove the `unsupported_format` returns for `.html` and `.pdf`. Wire to the existing parsers. Pass result through the same DuckDB/PostgreSQL pipeline that SMS XML already uses.
- **Risk:** Low — parsers exist, pipeline is proven with SMS.

#### T0-2: Port `production-message-schemas.ts` → Alpha 2 migrations
- **Alpha 1 source:** `drizzle/production-message-schemas.ts` (repo-only, not in zip)
- **Alpha 2 target:** `migrations/` — new migration file
- **What to do:** The Alpha 1 production schema has the canonical table definitions for `messaging_documents`, `messaging_conversations`, `messaging_messages`, `messaging_attachments`, `messaging_behaviors`, `messaging_evidence_items`, `messaging_factor_citations`, and the MCL factor + behavior category reference tables. Alpha 2's current schema (`migrations/001-005`) needs to be compared against this — merge in any fields Alpha 2 is missing, never drop Alpha 1 fields.
- **Fields Alpha 2 must not miss:** `mcl_factors[]` array on evidence items, `behavior_categories` with `mclFactors` mapping, `exhibit_number`, `relevance_score`, `timestamp_precision`, `direction` enum, `body_lower` (search), `content_hash` (SHA-256 per message), `previous_message_id`/`next_message_id` thread links.
- **Risk:** Medium — requires careful diff. Do NOT run migration until diff is verified.

---

### TIER 1 — Core Forensic Engine (Port Next — Outcome 2 + 3 Dependency)

#### T1-1: Port `pattern-analyzer.ts` → `py-mcp-server`
- **Alpha 1 source:** `server/mcp/forensics/pattern-analyzer.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/` — new file `forensics/pattern_analyzer.py`
- **What it contains:**
  - `BUILT_IN_MODULES` — 18 analysis modules (gaslighting, blame-shifting, threats, isolation, financial control, emotional blackmail, love bombing, DARVO, minimization, etc.)
  - `BUILT_IN_PATTERNS` — the actual regex pattern definitions keyed by module ID
  - `PatternMatch`, `AnalysisResult`, `Contradiction`, `TimelineEvent` type contracts
  - `LinguisticAnalysis` — pronoun ratios, hedge vs. certainty, sentence length overelaboration score
  - MCL 722.23 factor scoring per match
  - Full `analyze()` method with DB pattern loading + built-in fallback
- **Port note:** Alpha 1 has Drizzle ORM DB queries that are COMMENTED OUT in favor of SQL.js for dev. Port to Python with SQLAlchemy against Alpha 2's PostgreSQL. The `BUILT_IN_MODULES` and `BUILT_IN_PATTERNS` constants transfer directly.
- **Risk:** Medium — logic is pure, DB layer needs translation.

#### T1-2: Port `hurtlex-stream.ts` → `py-mcp-server`
- **Alpha 1 source:** `server/mcp/forensics/hurtlex-stream.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/forensics/hurtlex_stream.py`
- **What it contains:**
  - 17 hardcoded `HURTLEX_CATEGORIES` (PS, RCI, PA, DDF, DDP, DMC, IS, OR, AN, ASM, ASF, PR, OM, QAS, CDS, RE, SVP)
  - Streams from GitHub raw (`https://raw.githubusercontent.com/valeriobasile/hurtlex/master/lexica/EN/1.2/hurtlex_EN.tsv`)
  - 1-hour in-memory cache (no DB write — this is intentional)
  - `fetchTerms()`, `searchTerms()`, `matchText()`, `getCategoryCounts()`
  - Parses TSV: col 1=POS, col 2=category, col 4=lemma, col 5=level
- **Port note:** Straightforward Python translation. Keep no-DB-storage design as-is. Use `httpx` or `requests` for fetch, `functools.lru_cache` or manual TTL dict for cache.
- **Risk:** Low — pure logic, no DB dependency.

#### T1-3: Port `timeline-generator.ts` → `py-mcp-server`
- **Alpha 1 source:** `server/mcp/forensics/timeline-generator.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/forensics/timeline_generator.py`
- **What it contains:**
  - Timestamp extraction with 10 regex pattern types (absolute dates, ISO, US dates, relative days/weeks/months, day-of-week, special dates, temporal context)
  - `CycleOfAbuseInstance` detection — Lenore Walker's tension/incident/reconciliation/calm phases with regex indicator weights
  - `EscalationData` — weekly/monthly severity trend analysis (increasing/decreasing/stable)
  - `TimelineReport` with markdown report generation
  - Uses `compromise` NLP (Node.js) and `date-fns` — port to Python `dateparser` + `python-dateutil`
  - `CYCLE_PHASE_INDICATORS` — the weighted regex sets for each phase (100+ patterns)
- **Port note:** `compromise` NLP is JavaScript-only. Replace with `spaCy` for temporal expression extraction. `date-fns` maps directly to Python `dateutil`.
- **Risk:** Medium — NLP library swap, logic is well-defined.

#### T1-4: Port `multi-pass-classifier.ts` → `py-mcp-server`
- **Alpha 1 source:** `server/mcp/analysis/multi-pass-classifier.ts` + `server/mcp/analysis/nlp-classifier.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/analysis/multi_pass_classifier.py`
- **What it contains:**
  - Pass 0: `priority-screener.ts` — immediate flags for child name variants (Kailah/Kyla/Kaila/Kailuh), custody interference, call blocking, parental alienation
  - Pass 1: spaCy (structure, entities, attribution)
  - Pass 2: NLTK VADER (sentiment, negation, sarcasm via TextBlob subjectivity)
  - Pass 3: Pattern analyzer (custom patterns, MCL factors)
  - Pass 4: TextBlob (polarity, subjectivity)
  - Pass 5: Sentence Transformers (semantic similarity to known patterns)
  - Output: `MultiPassClassification` with speaker detection, sentiment consensus, patterns, linguistic features, severity 1-10, confidence 0-1
- **Port note:** Python-native — this was always meant to run in Python. `nlp_runner.py` in Alpha 1 already implements the Python side. Needs integration with pattern_analyzer port from T1-1. Priority screener patterns are hardcoded — port verbatim.
- **Risk:** Low — Python stack already exists in Alpha 1.

#### T1-5: Port `conversation-segmentation.ts` → `py-mcp-server`
- **Alpha 1 source:** `server/mcp/analysis/conversation-segmentation.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/analysis/conversation_segmentation.py`
- **What it contains:**
  - Cluster ID assignment: `PLAT_YYMM_TOPIC_iii` format (e.g., `SMS_2401_KAILAH_001`)
  - `PLATFORM_CODES` map (sms/imessage/facebook/messenger/email/chatgpt/whatsapp/discord/snapchat)
  - `TOPIC_CODES` map — 30+ topic keywords mapped to 6-char codes (KAILAH, VISITS, CALLS, SCHOOL, MONEY, HEALTH, SUBST, INFID, THREAT, etc.)
  - Topic detection via spaCy keyword extraction
- **Risk:** Low — pure logic.

---

### TIER 2 — New Sources Not In Alpha 2

#### T2-1: Port ChatGPT export parser
- **Alpha 1 source:** `utilities/scripts/chatgpt_parser.py`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/parsers/chatgpt_parser.py`
- **What it contains:** Full ChatGPT JSON export parser. `ConversationTurn`, `Entity`, `Artifact` dataclasses. Normalized schema output. spaCy entity extraction. Code block artifact extraction with language detection. SHA-256 per message. JSONL output.
- **Risk:** Low — already Python, minor adaptation.

#### T2-2: Port Snapchat parser (schema-first)
- **Alpha 1 source:** `server/mcp/schemas/snapchat_messages.json`
- **Alpha 2 target:** `mcp-servers/ts-mcp-server/src/tools/SnapchatExportParser.ts`
- **What it contains:** HTML export schema — `div.message` container, `.sender-name`, `.message-text`, `.timestamp`
- **Port note:** No parser implementation exists in Alpha 1 — only the schema. The HTML structure is documented. Port as new parser modeled on `FacebookExportParser.ts`, using the same cheerio pattern. Wire into `EvidenceIngestor.ts` alongside Facebook.
- **Risk:** Low — schema is defined, cheerio pattern established.

#### T2-3: Wire Facebook + Snapchat through `EvidenceIngestor` to `SmsEvidenceIngestor` pipeline equivalents
- **Alpha 2 target:** New `FacebookEvidenceIngestor.ts` and `SnapchatEvidenceIngestor.ts` modeled on `SmsEvidenceIngestor.ts`
- **Risk:** Low once T0-1 is done.

---

### TIER 3 — Infrastructure & Storage

#### T3-1: Port Cloudflare Workers
- **Alpha 1 source:** `deploy/cloudflare/` — 6 workers
  - `evidence-hasher.js` — REST API for chain-of-custody hashing at edge, KV-backed chain storage
  - `r2-storage.js` — R2 file upload/download/list/delete/presign
  - `auth-proxy.js` — Auth middleware
  - `rate-limiter.js` — Rate limiting
  - `cache-api.js` — Response caching
  - `webhook-receiver.js` — Inbound webhooks
- **Alpha 2 target:** `deploy/cloudflare/` (does not exist yet)
- **Port note:** These are Cloudflare Workers — runtime environment is already specified. Copy with `wrangler.toml`, update env var names to match Alpha 2.
- **Risk:** Low — self-contained Workers, environment variables are the only coupling.

#### T3-2: Alpha 1 Graphiti GCP deployment — DEFERRED (ROOF ITEM)
- **Alpha 1 source:** `deploy/gcp/graphiti/` — FastAPI + Graphiti-core on Cloud Run
- **Alpha 2 forensic graph decision:** Graphiti/Neo4j for evidence knowledge graph is **Semantica's domain** (ADR-007). Do not port as a Semantica substitute.
- **Future use case (separate problem):** Graphiti may be deployed as an **agent/model memory tool** — temporal facts, cross-session agent memory, entity persistence across Conductor workflow runs. This is architecturally distinct from the forensic evidence graph.
- **Deferred until:** Agent memory requirements are defined. Evaluate whether Graphiti, Zep, or a custom LanceDB+Neo4j memory layer is the right fit.
- **Action when revisiting:** Read `deploy/gcp/graphiti/main.py` in full. Assess against Conductor task memory requirements at that time.
- **Risk:** N/A — parked, not abandoned.

#### T3-3: Port Embedding Pipeline
- **Alpha 1 source:** `server/mcp/loaders/embedding-pipeline.ts` + `server/mcp/loaders/real-embedding-service.ts`
- **Alpha 2 target:** `mcp-servers/py-mcp-server/src/` — `embeddings/embedding_pipeline.py`
- **What it contains:**
  - `EmbeddingVector` + `EmbeddingMetadata` types — platform, chunk_index, offsets, case_id, evidence_id, participants, timestamp
  - `SemanticSearchQuery` + `SearchFilters` — platform[], case_id, evidence_id, participants, date_range
  - `RealEmbeddingService` — retry logic (3 attempts), batch processing (configurable batch size), OpenAI-compatible API format, handles both `data[0].embedding` and direct `embedding` response formats
  - pgvector SQL setup (`pgvector-setup.sql`) — HNSW index, `match_embeddings()` function with metadata filters
- **Port note:** Alpha 2 already uses LanceDB. The pgvector setup from Alpha 1 is relevant if/when Alpha 2 adopts pgvector for permanent vector storage. Port the `RealEmbeddingService` retry/batch logic into py-mcp-server now regardless.
- **Risk:** Medium — storage backend differs (LanceDB vs pgvector), but the embedding generation logic is storage-agnostic.

#### T3-4: Port `LexiconImporter` + `PluginRegistry`
- **Alpha 1 source:** `server/mcp/loaders/lexicon-importer.ts` + `server/mcp/plugins/registry.ts`
- **Alpha 2 target:** `mcp-servers/ts-mcp-server/src/` or `py-mcp-server/src/`
- **What it contains:**
  - `LexiconImporter` — generic GitHub/URL/local lexicon fetcher with conflict resolution, language filtering, category mapping. `LEXICON_REGISTRY` extensible config. Currently configured for HurtLex.
  - `PluginRegistry` — tool registration with tag indexing, semantic search by `query` + `topK` + `category` + `tags`, `PluginManifest` registration (bulk).
- **Risk:** Low — pure logic.

---

### TIER 4 — Utility Scripts

All located at `utilities/scripts/` in the Alpha 1 repo:

| Script | What it does | Alpha 2 target |
|---|---|---|
| `conversation_splitter.py` | Splits ChatGPT JSON exports by N conversations per chunk. Handles `{conversations: []}` and bare array formats. Windows UTF-8 safe. | `scripts/utilities/conversation_splitter.py` |
| `find_duplicates.py` | SHA-256-based duplicate file finder across directory tree | `scripts/utilities/find_duplicates.py` |
| `batch_json_splitter.py` | Batch-processes a directory of JSON files with configurable chunk size | `scripts/utilities/batch_json_splitter.py` |
| `output_schemas.py` | Validates JSONL output files against ConversationTurn/Entity/Artifact schemas | `scripts/utilities/output_schemas.py` |
| `clean_markdown_converter.py` | (Unread — needs read before port) | `scripts/utilities/` |
| `conversation_to_docx.py` | (Unread — needs read before port) | `scripts/utilities/` |
| `docx_to_pdf.py` | (Unread — needs read before port) | `scripts/utilities/` |
| `compare_nltk_vs_agent.py` | (Unread — comparison utility) | `scripts/utilities/` |
| `chunk_file_tool.py` | (Unread — chunking utility) | `scripts/utilities/` |
| `analyze_triggers.py` | Skill trigger anti-pattern analyzer — not relevant to forensics pipeline | SKIP |

---

## What to Leave in Alpha 1

These Alpha 1 components have direct Alpha 2 equivalents that are **more advanced** — do not port:

| Alpha 1 | Alpha 2 Equivalent | Why Alpha 2 Wins |
|---|---|---|
| `chain-custody.ts` (SHA-256 JSONL, file-based) | `evidence_signing.py` (Ed25519 cryptographic signatures, Pydantic models) | Ed25519 is legally stronger than SHA-256-only chaining |
| `evidence-hasher.ts` (plugin, file-based) | `hash_verification.py` (multi-algorithm, batch, Pydantic) | Alpha 2 is more complete |
| `message-schemas.ts` (stub schema) | Alpha 2 migrations 001-005 | Alpha 2 schema is more complete; use `production-message-schemas.ts` to fill gaps |
| Alpha 1 tRPC routers (`patterns.ts`, `settings.ts`) | Alpha 2 MCP tool surface | Architecture change — Alpha 2 is MCP-native, not tRPC |
| Alpha 1 React client (`client/`) | Alpha 2 CopilotKit + NLUX | Architecture change |
| Alpha 1 MySQL app layer (`drizzle/schema.ts` app tables) | Alpha 2 PostgreSQL + Directus | Architecture change |
| `server/mcp/tools/graphiti-memory.ts` (Graphiti MCP tools for evidence graph) | Semantica — `semantica_build_graph`, etc. | Semantica owns the forensic evidence graph (ADR-007). Flag stubs, do not work around. |
| `deploy/gcp/graphiti/` (Cloud Run FastAPI Graphiti API) | **DEFERRED — ROOF ITEM** | Possible future agent/model memory layer (cross-session, Conductor task memory). Architecturally distinct from forensic graph. Revisit when agent memory requirements defined. |
| `behavior-service.ts` (in-memory regex fallback, DB stub note) | T1-1 pattern_analyzer.py | Full port supersedes this |

---

## Port Execution Order

```
TIER 0 (unblock ingest — do NOW):
  T0-1: Wire EvidenceIngestor → FacebookExportParser + ImessagePdfParser
  T0-2: Diff production-message-schemas.ts vs Alpha 2 migrations, write gap migration

TIER 1 (forensic engine — after T0):
  T1-1: port pattern_analyzer.py
  T1-2: port hurtlex_stream.py      ← can run parallel with T1-1
  T1-3: port timeline_generator.py  ← depends on T1-1 (uses PatternMatch types)
  T1-4: port multi_pass_classifier.py ← depends on T1-1 + T1-2
  T1-5: port conversation_segmentation.py ← independent, can run anytime

TIER 2 (new sources — after T0):
  T2-1: port chatgpt_parser.py
  T2-2: build SnapchatExportParser.ts (schema exists, no Alpha 1 impl)
  T2-3: wire Facebook + Snapchat through EvidenceIngestor pipeline

TIER 3 (infrastructure — after T1):
  T3-1: port Cloudflare Workers (independent, no code dependency)
  T3-2: DEFERRED (ROOF) — Graphiti as agent/model memory tool. Not Semantica's job. Revisit when Conductor agent memory requirements are defined.
  T3-3: port embedding pipeline
  T3-4: port LexiconImporter + PluginRegistry

TIER 4 (utilities — anytime):
  All utility scripts — independent, no dependencies
```

---

## Files to Read Before Starting Each Tier

Before executing any tier, the agent MUST read these files (not yet fully read):

- **Before T0-2:** Full Alpha 2 migrations 001-005 (`/tmp/MCP_PLATFORM/migrations/`)
- **Before T1-1:** Full `pattern-analyzer.ts` — only read to line 360, `BUILT_IN_PATTERNS` constant not yet read
- **Before T1-3:** `CYCLE_PHASE_INDICATORS` in `timeline-generator.ts` — partially read, cut off at line 200
- **Before T2 scripts:** `clean_markdown_converter.py`, `conversation_to_docx.py`, `docx_to_pdf.py`, `chunk_file_tool.py`
- **Before T3-3:** Full `embedding-pipeline.ts` (VectorStore class not read) + `pgvector-setup.sql` full file

---

## Alpha 1 Assets That Don't Port (Architecture Mismatch)

These exist in Alpha 1 but have no equivalent in Alpha 2 and are NOT part of the Alpha 2 architecture:

- `server/mcp/storage/supabase-client.ts` — Alpha 2 uses DuckDB + PostgreSQL, not Supabase
- `server/mcp/storage/systemRouter.ts` (TrinityRouter) — Alpha 2 uses Conductor for orchestration
- `server/mcp/llm/smart-router.ts` — Alpha 2 uses LiteLLM
- `server/mcp/orchestration/` — Alpha 2 uses Conductor OSS
- `deploy/salem-trinity/` — Alpha 1's 3-VPS topology. Alpha 2 has its own deployment architecture.
- `server/mcp/workers/` — Alpha 1's worker pool. Alpha 2 uses Conductor tasks.
- `client/` React app — Alpha 2 uses CopilotKit + NLUX + OpenWebUI/LibreChat

---

## Alpha 1 Docs Worth Preserving in Alpha 2 Wiki

These Alpha 1 docs contain information that should be referenced or linked from the Alpha 2 wiki (not merged blindly — they describe Alpha 1 architecture, not Alpha 2):

- `docs/PROJECT_INTEL_SSOT.md` — canonical description of what this case/platform is
- `docs/analysis/GAP_ANALYSIS.md` — historical gap analysis
- `BACKEND_ARCHITECTURE.md` — dual-concern (app vs. evidence) explanation
- `docs/MCP_TOOL_CATALOG.md` — tool definitions, some of which should inform Alpha 2 tool naming
- `WHAT_IS_THIS_PROJECT.md` — one-paragraph mission statement, still accurate at a high level
- `drizzle/production-message-schemas.ts` — canonical schema reference for T0-2

---

*Read the repo before theorizing. This document is based on direct file reads of both Alpha 1 sources.*
