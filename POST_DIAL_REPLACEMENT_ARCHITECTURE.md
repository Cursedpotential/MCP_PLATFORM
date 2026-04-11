# Post-DIAL Replacement Architecture

> ⚠️ **PLANNING DOCUMENT — NOT AUTHORIZATION**: Nothing in this document is permission to implement. Each phase, major task, and architectural decision requires explicit owner approval before any code is written or any service is activated.

---

## Overview

This document describes the full system architecture of the MCP Platform post-DIAL stack. It covers component responsibilities, tool execution patterns, data flows, and the ingestion pipeline.

---

## Responsibility Matrix

| Component | Role | Port | Status |
|-----------|------|------|--------|
| **DIAL Core** | AI model gateway; routes model requests and MCP tool dispatches | 8080 | ✅ Operational |
| **DIAL Chat** | Developer/admin chat UI connected to DIAL Core | 3000 | ✅ Operational |
| **TS MCP Server** | Tool executor: parsers, DuckDB fingerprinting, PostgreSQL writes, format detection | 8081 | ✅ Operational |
| **Py MCP Server** | Tool executor: Semantica NLP, LanceDB vector ops, Neo4j graph writes, embeddings | 8082 | ✅ Operational |
| **JS MCP Server** | Tool executor: text utilities, format handlers, lightweight transformations | 8083 | ✅ Operational |
| **PostgreSQL** | Relational store: normalized evidence, analysis results, app data, pgvector index | 5432 | ✅ Operational |
| **DuckDB** | Embedded vault: SHA-256 fingerprints, UUIDv7 keys, dedup, WORM flags, master clock | — (embedded) | ✅ Operational |
| **LanceDB** | Embedded vector store: text embeddings, ANN search | — (embedded) | ✅ Operational |
| **Neo4j** | Knowledge graph: entities, relations, temporal facts (valid_from/valid_to) | 7687 | ⚠️ Configured, not populated |
| **Keycloak** | OIDC/JWT provider: authentication, authorization, role management | 8180 | ✅ Operational |
| **Directus** | User-facing data/admin surface: evidence browser, REST/GraphQL over PostgreSQL | 8055 | ⚠️ In compose, needs activation approval |
| **CopilotKit** | Embedded HITL evidence review chat (`client/`) | 3002/5173 | ⚠️ Stub wired |
| **OpenWebUI** | Remote chat interface federating with DIAL Core | 3001 | 🔜 Planned (needs activation approval) |
| **LibreChat** | Alternative remote chat interface with document upload | 3003 | 🔜 Planned (needs activation approval) |
| **Caddy** | HTTPS termination, reverse proxy routing, TLS certificate management | 80/443 | ✅ Operational |
| **Dragonfly** | Redis-compatible in-memory cache (sessions, rate limiting, pub/sub) | 6379 | ✅ Operational |
| **WunderGraph Cosmo** | GraphQL federation gateway over subgraphs | 4000 | ✅ Operational |

---

## Tool Execution: Document Intelligence Router

The document intelligence router is a pluggable component in the Py MCP Server. It sits between the `ingest_evidence` tool and the raw document processing engines.

```
ingest_evidence (MCP Tool)
        │
        ▼
  EngineRouter
  ┌─────────────────────────────────────────────────────┐
  │  1. Detect document type (MIME, extension, content) │
  │  2. Select best available local engine              │
  │  3. Fall back through chain if engine fails         │
  │  4. Fall back to cloud engine (if approved + wired) │
  │  5. Return structured extraction result             │
  └─────────────────────────────────────────────────────┘
        │
        ├── Pandoc      [local]  ⚠️ stub → activation needed
        ├── Tesseract   [local]  ⚠️ stub → activation needed
        ├── DocTR       [local]  ⚠️ stub only
        ├── Docling     [local]  ⚠️ stub only
        ├── OCRopus     [local]  ⚠️ stub only
        ├── Unstructured [local/API] ⚠️ stub only
        ├── GLM-OCR     [local]  🔜 planned
        ├── LlamaParse  [cloud]  ❌ deferred
        ├── Google DocAI [cloud] ❌ deferred
        ├── AWS Textract [cloud] ❌ deferred
        └── IBM watsonx [cloud]  ❌ deferred
```

**Routing priority**: Local engines first (cost = $0, no data egress). Cloud engines only when (a) local engines cannot process the document and (b) owner has explicitly approved cloud activation.

---

## Data Flow Diagram

```
                        ┌─────────────────────────────────────┐
                        │           CLIENT LAYER              │
                        │  CopilotKit │ OpenWebUI │ LibreChat │
                        │  DIAL Chat  │  Directus             │
                        └──────────────┬──────────────────────┘
                                       │ HTTPS (Caddy)
                        ┌──────────────▼──────────────────────┐
                        │         DIAL CORE (8080)            │
                        │  Model routing │ Auth (Keycloak JWT) │
                        │  MCP dispatch  │ WunderGraph Cosmo   │
                        └───┬───────────┬───────────┬─────────┘
                            │           │           │
               ┌────────────▼──┐  ┌─────▼───┐  ┌───▼────────┐
               │ TS MCP (8081) │  │Py MCP   │  │JS MCP      │
               │ Parsers       │  │(8082)   │  │(8083)      │
               │ DuckDB writes │  │Semantica│  │Utilities   │
               │ PG writes     │  │LanceDB  │  │Text tools  │
               └───┬───────────┘  │Neo4j    │  └────────────┘
                   │              └────┬────┘
                   │                  │
          ┌────────▼──────────────────▼────────────────────┐
          │                STORAGE TIER                     │
          │  DuckDB (embedded)  │  LanceDB (embedded)       │
          │  PostgreSQL (5432)  │  Neo4j (7687)             │
          └────────────────────────────────────────────────┘
```

---

## Ingestion Pipeline Flow

```
1. CLIENT submits evidence (file upload or raw content)
         │
         ▼
2. DIAL CORE receives request, validates JWT (Keycloak)
         │
         ▼
3. DIAL CORE dispatches ingest_evidence MCP tool → TS MCP Server
         │
         ▼
4. TS MCP Server: FORMAT DETECTION
   ├── SMS XML?      → SMS XML Parser
   ├── Facebook JSON? → Facebook Parser
   ├── iMessage?     → iMessage Parser
   └── Document?     → EngineRouter (Py MCP Server)
         │
         ▼
5. PARSER/ROUTER extracts structured content → EvidenceBatch
         │
         ▼
6. TS MCP Server: FINGERPRINTING (SHA-256 computed NOW, before any modification)
         │
         ▼
7. DuckDB: DEDUP CHECK (has this SHA-256 been seen before?)
   ├── DUPLICATE → log + return existing UUID, stop
   └── NEW → continue
         │
         ▼
8. DuckDB: WRITE fingerprint record (UUIDv7 + SHA-256 + timestamp)
         │
         ▼
9. PostgreSQL: WRITE normalized EvidenceBatch records
         │
         ▼
10. Py MCP Server: EMBED (text → vector via sentence-transformers)
         │
         ▼
11. LanceDB: WRITE embedding vectors
         │
         ▼
12. PostgreSQL (pgvector): WRITE embedding vectors (fallback index)
         │
         ▼
13. Return ingestion result to DIAL CORE → CLIENT
    (UUID, SHA-256, record count, any warnings)
```

---

## Evidence Chain of Custody Flow

```
EVIDENCE RECEIVED
      │
      ▼
[SHA-256 computed] ──────────────────────────────────────────► DuckDB vault
      │                                                         (immutable record)
      ▼
[EvidenceBatch created] ─────────────────────────────────────► PostgreSQL
      │                                                         (audit_log row)
      ▼
[Pass 1 analysis triggered] ─────────────────────────────────► PostgreSQL
      │                                                         (pass1_results, WORM flag in DuckDB)
      ▼
[HITL Review Queue] ──────────────────────────────────────────► ReviewQueue
      │                                                         (review_queue row)
      ▼
[Reviewer approves/annotates] ───────────────────────────────► PostgreSQL
      │                                                         (review_decisions row)
      ▼
[Pass 2 analysis — if triggered] ────────────────────────────► PostgreSQL
      │                                                         (pass2_results row, references Pass 1)
      ▼
[Chain of custody report] ───────────────────────────────────► Generated from DuckDB + PostgreSQL audit log
```

**Invariants**:
- SHA-256 is computed before any transformation. The hash must match the original bytes.
- Pass 1 records are never modified after write. Corrections go into Pass 2 with explicit references.
- Every state transition has an audit log entry with actor identity (from Keycloak JWT), timestamp, and action.
- DuckDB is the canonical source of truth for fingerprints. PostgreSQL is the operational evidence store.

---

## Authentication Flow

```
CLIENT REQUEST
      │
      ▼
[Caddy] — TLS termination
      │
      ▼
[DIAL Core] — extracts Bearer token from Authorization header
      │
      ▼
[Keycloak] — validates JWT, checks realm/client, extracts roles
      │
      ├── UNAUTHORIZED (401) → reject immediately
      └── AUTHORIZED → attach claims to request context
                │
                ▼
         [MCP tool dispatch — roles checked again at tool level]
```

---

## Service Port Reference

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| DIAL Core | 8080 | HTTP/WS | Internal only; Caddy proxies external traffic |
| DIAL Chat | 3000 | HTTP | Dev/admin UI |
| TS MCP Server | 8081 | HTTP | Internal only |
| Py MCP Server | 8082 | HTTP | Internal only |
| JS MCP Server | 8083 | HTTP | Internal only |
| PostgreSQL | 5432 | TCP | Internal only |
| Neo4j (Bolt) | 7687 | Bolt | Internal only |
| Neo4j (HTTP) | 7474 | HTTP | Internal only (browser) |
| Keycloak | 8180 | HTTP | Internal; Caddy proxies /auth |
| WunderGraph Cosmo | 4000 | HTTP/WS | Internal; Caddy proxies /graphql |
| Directus | 8055 | HTTP | Internal; Caddy proxies /admin ⚠️ needs approval |
| Dragonfly/Redis | 6379 | TCP | Internal only |
| Caddy HTTP | 80 | HTTP | Public; redirects to HTTPS |
| Caddy HTTPS | 443 | HTTPS | Public entry point |

---

## Network Topology

All services communicate on an internal Docker bridge network (`mcp-platform-network`). Services do not bind to `0.0.0.0` directly — they bind to the internal network, and Caddy is the sole public-facing component. Keycloak validates all inbound requests. No service-to-service call bypasses Keycloak for requests that carry user identity.

---

*Last updated: see git log*
