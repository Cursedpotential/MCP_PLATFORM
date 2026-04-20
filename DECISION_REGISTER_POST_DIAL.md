# Decision Register — Post-DIAL Architecture

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Purpose

This register records architectural decisions (ADRs) made for the MCP Platform post-DIAL architecture. Entries are append-only. Superseded decisions reference their replacement.

---

## ADR Format

```
## ADR-XXX: [Title]
**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Deferred | Superseded]
**Needs owner approval?** [yes | no]
**Decision:** ...
**Rationale:** ...
**Consequences:** ...
```

---

## ADR-001: DIAL Core as Primary AI Gateway

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All AI model routing flows through DIAL Core on port 8080.
**Rationale:** Centralized gateway provides observability, authentication, and model switching without client changes.
**Consequences:** All MCP servers register with DIAL Core. No direct model API calls from application code.

---

## ADR-002: MCP Protocol for Tool Execution

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All tool execution uses the Model Context Protocol (MCP) over the three dedicated servers.
**Rationale:** MCP provides a standard interface for tool registration and invocation that DIAL Core natively supports.
**Consequences:** New tools must be registered as MCP tools, not as ad-hoc HTTP endpoints.

---

## ADR-003: Three-Server MCP Architecture

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Tools are split across three MCP servers: TypeScript (parsers, storage), Python (NLP, graph), JavaScript (utilities).
**Rationale:** Language-native tooling for each concern. TypeScript for Node.js I/O and type safety; Python for ML/NLP ecosystem; JavaScript for lightweight utilities.
**Consequences:** Cross-server tool chains require DIAL Core orchestration.

---

## ADR-004: DuckDB as Fingerprint Vault

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** DuckDB is the source of truth for SHA-256 content fingerprints, UUIDv7 primary keys, deduplication, and WORM flags.
**Rationale:** DuckDB is embedded (no network), fast for analytical queries, and supports immutable patterns.
**Consequences:** All evidence must pass through DuckDB fingerprint check before PostgreSQL write.

---

## ADR-005: PostgreSQL as Evidence Store

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** PostgreSQL with pgvector extension is the primary relational store for evidence, analysis results, and application data.
**Rationale:** Well-understood, ACID-compliant, supports vector search via pgvector, and integrates with Directus.
**Consequences:** All normalized evidence and Pass 1/Pass 2 analysis results live in PostgreSQL.

---

## ADR-006: LanceDB for Vector Embeddings

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** LanceDB is the primary vector store for text embeddings.
**Rationale:** LanceDB is embedded (no network), fast for ANN search, and integrates well with the Python ecosystem.
**Consequences:** Embeddings are written to LanceDB immediately after ingestion. pgvector serves as fallback.

---

## ADR-007: Neo4j for Knowledge Graph

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Neo4j is the knowledge graph store for entities, relations, and temporal facts.
**Rationale:** Graph databases are the natural fit for entity-relation-temporal data that would require complex joins in PostgreSQL.
**Consequences:** NER extraction and relation extraction pipelines must write to Neo4j. Graph population gated on pipeline approval.

---

## ADR-008: Keycloak for OIDC/JWT

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Keycloak is the sole OIDC/JWT provider for all services.
**Rationale:** Single auth provider simplifies token validation and role management across services.
**Consequences:** All new services must register as Keycloak clients. No service may be externally exposed without Keycloak gating.

---

## ADR-009: Caddy for HTTPS and Routing

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Caddy handles TLS termination and reverse proxy routing for all HTTP services.
**Rationale:** Caddy's automatic TLS and simple configuration reduce operational overhead.
**Consequences:** All external-facing ports route through Caddy. Services bind to localhost only.

---

## ADR-010: WunderGraph Cosmo for GraphQL Federation

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** WunderGraph Cosmo provides GraphQL federation across subgraphs on port 4000.
**Rationale:** Federation allows each service to own its GraphQL schema while presenting a unified graph to clients.
**Consequences:** Deterministic, audited operations use Cosmo. Ad-hoc exploratory queries use MCP tools directly.

---

## ADR-011: SHA-256 at First Touch

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** SHA-256 fingerprint is computed immediately upon evidence ingestion, before any processing.
**Rationale:** The hash must reflect the original, unmodified evidence content to be forensically valid.
**Consequences:** No pre-processing (normalization, encoding conversion) may occur before the SHA-256 is computed and stored.

---

## ADR-012: WORM for Pass 1 Records

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Pass 1 analysis records are write-once, read-many (WORM). Once written, they cannot be modified.
**Rationale:** Pass 1 represents the unbiased, context-limited first analysis. Modifications would compromise forensic integrity.
**Consequences:** Pass 1 records get immutable flags in DuckDB. Any correction requires a new Pass 2 record with explicit audit trail.

---

## ADR-013: Alpha 1 Code as Reference, Not Destination

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Alpha 1 code in `MCP_Tool_Platform/` is read-only reference material. Port proven logic; never modify Alpha 1 files.
**Rationale:** Alpha 1 is the production-tested baseline. Modifying it risks losing the reference point.
**Consequences:** All agents must check Alpha 1 before building anything new. `MCP_Tool_Platform/` is never written to.

---

## ADR-014: Lazy Database Initialization

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All database connections use lazy initialization — connections are established on first use, not at service startup.
**Rationale:** Improves startup time and resilience when a database tier is temporarily unavailable.
**Consequences:** Services do not fail fast on startup if a database is down. Health checks must explicitly probe each tier.

---

## ADR-015: UUIDv7 Primary Keys

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All primary keys use UUIDv7 (time-sortable UUID).
**Rationale:** UUIDv7 provides globally unique identifiers that are also time-sortable, enabling efficient range queries.
**Consequences:** No auto-increment integer keys. All ID generation must use the UUIDv7 generator.

---

## ADR-016: EvidenceBatch as the Normalized Output Contract

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All parsers produce a normalized `EvidenceBatch` object with confidence scores.
**Rationale:** A shared output contract allows the ingestion pipeline to handle all parser types identically.
**Consequences:** New parsers must conform to the `EvidenceBatch` schema. Schema changes require a migration plan.

---

## ADR-017: Coordinator Pattern for Evidence Operations

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All evidence operations flow through a coordinator. No direct database access from tools.
**Rationale:** The coordinator enforces fingerprinting, dedup, chain of custody, and WORM rules uniformly.
**Consequences:** Tools that bypass the coordinator are non-compliant. Code review must catch direct DB writes from tool handlers.

---

## ADR-018: Dual Retrieval Pattern

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Known deterministic queries route to WunderGraph Cosmo; ad-hoc exploratory queries route to MCP tools.
**Rationale:** Cosmo operations are audited and reproducible; MCP tools are flexible but less auditable.
**Consequences:** High-stakes evidence queries must use Cosmo operations. Agent-driven exploration uses MCP tools.

---

## ADR-019: W3C PROV-O for Provenance Chains

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** Provenance chains follow the W3C PROV-O ontology.
**Rationale:** PROV-O is a standards-based, interoperable format for provenance that has legal acceptance.
**Consequences:** Provenance records must be expressible as PROV-O triples. Implementation is gated on NLP pipeline approval.

---

## ADR-020: Docker Compose for Local Development

**Date:** 2024-01-01
**Status:** Accepted
**Needs owner approval?** no
**Decision:** All services run in Docker Compose for local development. No bare-metal service requirements.
**Rationale:** Docker Compose provides a reproducible, isolated environment consistent across developer machines.
**Consequences:** Service configuration lives in `docker-compose.yml`. Production deployment (if ever) requires a separate strategy.

---

## ADR-021: Directus as User-Facing Data/Admin Surface

**Date:** 2025-01-01
**Status:** Accepted
**Needs owner approval?** yes — activation requires owner approval
**Decision:** Directus is accepted as the user-facing data browser and admin surface, connecting to PostgreSQL.
**Rationale:** Directus provides a no-code data management UI, auto-REST, and auto-GraphQL over PostgreSQL without requiring custom frontend development for data browsing tasks. It reduces the surface area of custom code that needs to be maintained.
**Consequences:** Directus container is added to `docker-compose.yml`. Activation requires owner approval. Evidence tables must be exposed as read-only or with strict access controls. Directus migrations must not conflict with the Alpha 2 PostgreSQL schema.

---

## ADR-022: SurrealDB Deferred for Future Evaluation

**Date:** 2025-01-01
**Status:** Deferred
**Needs owner approval?** yes — if reconsidered
**Decision:** SurrealDB is not included in the current architecture. Evaluation deferred to a future phase.
**Rationale:** SurrealDB's multi-model capabilities (document + graph + relational) are theoretically interesting but do not justify adding a fifth database technology at this stage. The current four-tier stack (DuckDB + PostgreSQL + LanceDB + Neo4j) covers all current requirements.
**Consequences:** No SurrealDB container. No SurrealDB client libraries. If a compelling use case emerges, this ADR should be revisited with a focused proposal.

---

## ADR-023: Multi-Engine Document Intelligence Architecture

**Date:** 2025-01-01
**Status:** Accepted
**Needs owner approval?** yes — individual engine activations require owner approval
**Decision:** The document intelligence system uses a pluggable router architecture, not a monolithic single-engine approach. All 11 engines (Pandoc, Tesseract, DocTR, Docling, OCRopus, Unstructured, LlamaParse, Google DocAI, AWS Textract, GLM-OCR, IBM watsonx) are supported as optional plugins behind a common `EngineRouter` interface.
**Rationale:** No single document intelligence engine is best for all document types. A router allows the system to select the best available engine for each document based on type, quality requirements, and cost/privacy constraints. A pluggable design means cloud engines can be added without modifying core logic.
**Consequences:** The `EngineRouter` is the single entry point for all document processing. Engines are opt-in — only engines with available runtimes or credentials activate. The router must implement a fallback chain. See `docs/architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md` for the full design.

---

## ADR-024: Document Intelligence Engines Are Opt-In

**Date:** 2025-01-01
**Status:** Accepted
**Needs owner approval?** yes — each engine activation requires owner approval
**Decision:** Document intelligence engines do not activate automatically. Each engine must be explicitly enabled via configuration, and cloud engines additionally require owner approval before credentials are wired.
**Rationale:** Preventing accidental data egress to cloud APIs is a critical requirement for a forensic evidence platform. Opt-in ensures no data leaves the local environment without deliberate action.
**Consequences:** The default configuration activates only engines with zero network dependencies (no cloud engines). Cloud engine configurations are stubbed but not populated. Activation of any cloud engine requires a documented approval in this register.

---

## ADR-025: Messaging Schemas — Port from Alpha 1 with Alpha 2 Extensions

**Date:** 2025-01-01
**Status:** Accepted
**Needs owner approval?** yes — port execution requires owner approval
**Decision:** Messaging parser schemas are ported from Alpha 1 `production-message-schemas.ts`, with the following Alpha 2 additions merged in: pgvector embedding fields, `device_id` tracking, and WAL-compatible column definitions.
**Rationale:** Alpha 1 `production-message-schemas.ts` represents production-tested field mappings for SMS, Facebook, and iMessage formats. Rewriting from scratch risks losing edge-case handling that was discovered in production. The Alpha 2 additions (embeddings, device tracking, WAL) do not conflict with Alpha 1 core fields.
**Consequences:** The porting agent must read Alpha 1 `production-message-schemas.ts` before writing any schema code. Alpha 1 source must not be modified. The merged schema must pass tests against both Alpha 1 fixture data and Alpha 2 database column expectations.

---

## ADR-026: UI Chat Interfaces — CopilotKit + OpenWebUI + LibreChat

**Date:** 2025-01-01
**Status:** Proposed
**Needs owner approval?** yes — all three require owner approval before activation
**Decision:** The platform supports three federated chat interfaces: (1) CopilotKit React module for embedded HITL evidence review (`client/`); (2) OpenWebUI as a remote chat surface federated with DIAL Core; (3) LibreChat as an alternative remote chat surface with document upload support. All three route through DIAL Core. None may be externally exposed without Keycloak gating.
**Rationale:** Different use cases require different chat interfaces. The embedded CopilotKit module is tightly integrated with the evidence review workflow. OpenWebUI and LibreChat serve as general-purpose interfaces for operators who prefer a standalone chat experience. Using multiple interfaces against a single DIAL Core gateway prevents model/tool lock-in to any single UI.
**Consequences:** CopilotKit stub is already in `client/`. OpenWebUI and LibreChat container definitions must be added to `docker-compose.yml` but kept disabled (commented out or with `profiles`) until owner approval. All three must register as Keycloak clients before activation. No UI may be exposed on a public port without Keycloak protection.

---

*Last updated: see git log*

---

## ADR-027: Open Structured Memory as Canonical Memory System

**Date:** 2026-04-20
**Status:** Accepted
**Needs owner approval?** No — architectural decision made by owner
**Decision:** Open Structured Memory (markdown files committed to the repository) is the canonical memory system for agent context persistence. Mem0 and ClaudeMem are not the primary systems and should not be relied upon as the source of truth.
**Rationale:** MD-based memory has no API dependency, no server to be up, no MCP tool call that might fail. Every agent in every tool with filesystem access can read it. It commits with the codebase, travels with clones, and is auditable via git history. Mem0 and ClaudeMem had inconsistent retrieval — agents skipped them or read wrong results.
**Consequences:** Memory lives in `memory/MEMORY.md` (root) and `[workdir]/memory/MEMORY.md` (per-domain). Agents must read memory files as part of mandatory session start. Agents must commit updated memory files at session end. MCP memory tool calls are supplementary, not primary.

---

## ADR-028: Hierarchical Memory Architecture

**Date:** 2026-04-20
**Status:** Accepted
**Needs owner approval?** No
**Decision:** Memory is organized as a hierarchy mirroring the directory structure. Root `memory/MEMORY.md` tracks platform-level session state. Each major subdirectory has its own `memory/MEMORY.md` tracking domain-specific state. Deeper = more specific. All use the same session log template.
**Rationale:** A flat single memory file becomes too long and too broad for agents working in specific domains. Domain-specific memory files let a TS server agent track parser work without reading Python server history. The hierarchy prevents memory from becoming a monolithic dump that agents stop reading.
**Consequences:** Memory files exist at: root, mcp-servers/, ts-mcp-server/, py-mcp-server/, js-mcp-server/, infrastructure/, client/, docs/. All use the same session log template. Agents commit their domain memory file plus root if platform-level decisions were made.

---

## ADR-029: GROUND_TRUTH.md as Mandatory First Read

**Date:** 2026-04-20
**Status:** Accepted
**Needs owner approval?** No
**Decision:** `GROUND_TRUTH.md` at repo root is the mandatory first read for every agent every session, after `git pull`. It is the single source of truth for current platform state — what runs, what doesn't, what's decided, what's open. All other planning documents are secondary and may be stale.
**Rationale:** Agents were making decisions based on outdated planning documents (SPRINT_PLAN.md, IMPLEMENTATION_PHASE_PLAN.md) that referenced deprecated architecture. A single authoritative state file that Matt maintains eliminates this ambiguity.
**Consequences:** GROUND_TRUTH.md must be kept current by Matt. When platform state changes (container starts, decision made, phase completes), GROUND_TRUTH.md is updated first. Agents that act on information from other planning docs without cross-checking GROUND_TRUTH.md are in violation of protocol.

---

## ADR-030: Platform Components Are Peers — No Orchestration Hierarchy

**Date:** 2026-04-20
**Status:** Accepted
**Needs owner approval?** No
**Decision:** Agno, n8n, Directus, and the MCP servers (TS/Py/JS) are peers. No single component orchestrates all others. Agno is the future orchestration glue for intelligent agent workflows but is not yet deployed and does not have authority over other components.
**Rationale:** Early design documents implied Agno was the top-level orchestrator, leading agents to design integrations that assumed Agno-primary hierarchy. This created dependency debt on a component that isn't deployed. The correct model is: each component has a defined responsibility, they coordinate through well-defined interfaces, and no component is subordinate to another.
**Consequences:** Agent prompts and documentation must not depict Agno as a controller over other components. Architecture diagrams must show peers. When Agno is eventually deployed, its integration must be designed through interfaces, not by modifying other components to serve it.

---

## ADR-031: Two Access Surfaces — MCP External and Internal API Direct

**Date:** 2026-04-20
**Status:** Accepted
**Needs owner approval?** No
**Decision:** The platform exposes two access surfaces: (1) MCP surface — external tools (OpenWebUI, LibreChat, Claude Code, OpenCode) connect via MCP protocol through Context Forge and Keycloak; (2) Internal API surface — Agno, n8n, and Directus connect directly to internal APIs without the MCP hop. The internal API is the canonical interface. MCP tools are thin wrappers over it.
**Rationale:** Building MCP tools as the primary interface and internal APIs as an afterthought couples business logic to the protocol layer. If MCP is the wrapper, the internal API can be tested, versioned, and consumed by multiple surfaces independently. This also means internal consumers (Agno, n8n) get lower latency and richer error handling than the MCP protocol allows.
**Consequences:** Internal API must be designed before or alongside MCP tool wrappers — not after. MCP tool implementations should be thin: validate inputs, call internal API, return result. Business logic lives in internal API handlers.

---

## ADR-032: OpenCode Deployment Model Is an Open Architectural Question

**Date:** 2026-04-20
**Status:** Open — awaiting owner decision
**Needs owner approval?** Yes — decision required before any implementation
**Decision:** The deployment model for OpenCode (server mode vs. agent mode) has not been decided. No implementation work may begin on OpenCode integration until Matt makes this decision.
**Rationale:** Server mode and agent mode have different implications for how models are invoked, how context is managed, how cost is controlled, and how the platform integrates with OpenCode. Implementing against an assumed model and then having to reverse course wastes significant effort.
**Consequences:** Agents must not implement any OpenCode integration. If a task touches OpenCode deployment, it must stop and flag OQ-1 as a blocker. When Matt decides, this ADR will be updated to Accepted with the chosen approach, and implementation can begin.

---

*Last updated: 2026-04-20*
