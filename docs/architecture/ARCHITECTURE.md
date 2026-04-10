---
title: Architecture Reference
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# AI DIAL Stack Architecture

> `MCP_Tool_Platform` remains a read-only legacy source. This document describes the checked-in `dial-stack` repository as it exists now and calls out planned gaps explicitly.

## Overview

The current stack is a containerized AI DIAL deployment with three MCP servers, PostgreSQL, Dragonfly, Keycloak, and supporting services. The TypeScript server owns parsing, DuckDB vault operations, PostgreSQL writes, admin tools, and review queue actions. The Python server owns Semantica, Neo4j, LanceDB, DPK-derived analysis, voice fingerprinting, placeholder behavioral detection, and workflow orchestration. The JavaScript server is present but still minimal.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`

## Architecture

```mermaid
graph TD
    U["User or operator"] --> C["Caddy proxy<br>infrastructure/Caddyfile"]
    C --> CHAT["DIAL Chat<br>docker-compose.yml"]
    C --> CORE["DIAL Core<br>infrastructure/core/config.json"]
    CORE --> TS["TS MCP server<br>mcp-servers/ts-mcp-server/src/index.ts"]
    CORE --> PY["Py MCP server<br>mcp-servers/py-mcp-server/src/server.py"]
    CORE --> JS["JS MCP server<br>mcp-servers/js-mcp-server/src/index.js"]
    CORE --> KC["Keycloak<br>docker-compose.yml"]
    TS --> PG["PostgreSQL"]
    TS --> DUCK["DuckDB vault"]
    PY --> NEO["Neo4j"]
    PY --> LANCE["LanceDB"]
```

The core runtime is defined in `docker-compose.yml`. `infrastructure/core/config.json` wires model routes, applications, and API-key roles into AI DIAL. `infrastructure/settings/settings.json` adds Keycloak-backed identity provider settings. Caddy currently fronts the stack on port 80 with reverse-proxy routing; the configuration comments mention HTTPS, but the checked-in file does not yet define a full TLS deployment.

Sources: `docker-compose.yml`, `infrastructure/core/config.json`, `infrastructure/settings/settings.json`, `infrastructure/Caddyfile`

## Modules

### Runtime and Routing

- DIAL core, chat, themes, auth-helper, analytics, and Caddy live in the container stack.
- Model routing currently includes OpenRouter-backed entries and one local Ollama entry that appears to conflict with the project rule against local LLM hosting.

Sources: `docker-compose.yml`, `infrastructure/core/config.json`, `CLAUDE.md`

### TypeScript MCP Server

- 18 live tools are exposed.
- Responsibilities: parsing, DuckDB vault operations, PostgreSQL access, provider/prompt administration, and HITL review queue management.
- Lazy singleton wrappers for vault, PostgreSQL, admin, and review services exist, but dispatch still uses a large `switch`.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`

### Python MCP Server

- 26 live tools are exposed through FastMCP.
- Responsibilities: Semantica entity/graph/provenance operations, LanceDB vector operations, Neo4j access, DPK preprocessing, voice fingerprinting, placeholder user-detection tools, and configurable workflows.
- Additional helper modules exist under `src/tools/` but are not all registered as MCP tools.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/`

### JavaScript MCP Server

- Only `ping_js_server` is live.
- The server is a placeholder for future document-processing or legacy wrappers.

Sources: `mcp-servers/js-mcp-server/src/index.js`

### Frontend

- The frontend is currently a Vite starter-style React app with CopilotKit and Radix dependencies installed.
- The evidence-review UI described in earlier planning docs has not yet been implemented in the checked-in client code.

Sources: `client/package.json`, `client/src/App.tsx`, `client/src/main.tsx`

## Data Surfaces

### Forensic Ingestion State

DuckDB is the intended first-touch forensic vault for hashes, ingestion status, and tier-write tracking through the TS MCP server.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/DuckDbVault.ts`

### Relational Records

PostgreSQL stores structured records and app-facing data reachable through the TS MCP tools and compose bootstrap SQL.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `infrastructure/init/postgres/01-init.sql`, `infrastructure/init/postgres/02-identification-tools.sql`, `infrastructure/init/postgres/03-tool-execution-log.sql`

### Graph and Vector State

Neo4j and LanceDB are managed through the Python MCP server for graph traversal, temporal facts, and semantic retrieval.

Sources: `mcp-servers/py-mcp-server/src/server.py`

### Workflow Configuration

Workflow presets live in JSON and are interpreted by the Python workflow tools at runtime.

Sources: `mcp-servers/py-mcp-server/config/workflows.json`, `mcp-servers/py-mcp-server/src/tools/workflow_tools.py`

## Implemented vs Planned

- Implemented now: DIAL runtime, TS/py/js MCP servers, parser coverage for SMS/Facebook/iMessage PDF, review/admin tools, Python semantic and identification tooling, Keycloak service scaffolding.
- Planned or partial: true analyst frontend, broader parser coverage, federated WunderGraph layer, full HTTPS deployment, and several advanced forensic workflows.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `client/src/App.tsx`

## Also See

- [Documentation Index](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/INDEX.md)
- [Development Guide](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/guides/DEVELOPMENT.md)
- [Roadmap](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/plans/ROADMAP.md)
- [Wiki Home](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/INDEX.md)
- [Stories](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/STORIES.md)
- [FAQ](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/FAQ.md)

## Change Log

- 2026-04-08, rev 2, Codex: replaced aspirational architecture text with a checked-in-code view and explicit planned-gap language.
  │              │   ├─ Tool routing (TS/Py/JS MCP)
  │              │   └─ Parallel tool execution
  │              ├─→ Query Execution
  │              │   ├─ DuckDB scans (time-series)
  │              │   ├─ Neo4j Cypher (graph traversal)
  │              │   ├─ PostgreSQL SQL (joins)
  │              │   └─ LanceDB vectors (similarity)
  │              └─→ Return flexible result
  │
  └─→ Frontend Display
       ├─ DIAL Chat (for developers)
       ├─ Custom React (for analysts with CopilotKit HITL)
       └─ Both support streaming responses + evidence UI
```

---

## Authentication & Security

### OIDC with Keycloak

1. **User Login**
   - Browser → Keycloak (port 8180)
   - Keycloak issues JWT token
   - Token stored in browser localStorage / HttpOnly cookie

2. **Token Validation**
   - Requests to DIAL Core include `Authorization: Bearer {jwt}`
   - DIAL Core validates token against Keycloak JWKS endpoint
   - Role extraction from JWT: `realm_access.roles`

3. **Role-Based Access Control (RBAC)**
   - Roles defined in Keycloak realm
   - Examples: `admin`, `analyst`, `readonly`
   - Enforced at DIAL Core level + optional GraphQL schema level

4. **Configuration** (in `infrastructure/settings/settings.json`)
   ```json
   {
     "identityProviders": {
       "keycloak": {
         "jwksUrl": "http://keycloak:8080/realms/dial/protocol/openid-connect/certs",
         "issuerPattern": "^http://localhost:8080/realms/dial$",
         "rolePath": "realm_access.roles",
         "disableJwtVerification": false
       }
     }
   }
   ```

### API Key Roles

For programmatic access (scripts, integrations):

| Role | Permissions | Use Case |
|------|-----------|----------|
| `admin` | Full read/write, schema changes, user management | Development, operations |
| `default` | Read/write evidence, execute tools | Standard analysts |
| `readonly` | Read-only access to all data | Auditors, viewers |

### HTTPS & Reverse Proxy

- **Caddy** (port 80/443) terminates HTTPS
- Automatic self-signed cert generation (development)
- Routes all traffic through `/chat`, `/api` prefixes
- Protects internal services from direct exposure

---

## Frontend Architecture

### 1. DIAL Chat (port 3000)

Official DIAL Chat UI provided by EPAM. Best for:
- Development and debugging
- Admin tasks
- Quick exploration
- Team collaboration

**Capabilities:**
- Conversation history
- Prompt templates
- Model selection
- Application marketplace
- File attachments

### 2. Custom React App + CopilotKit (port 5173)

Custom single-page application built in-house. Best for:
- **Human-in-the-Loop (HITL) review workflows**
- Evidence analysis with AI assistance
- Interactive evidence tagging
- Custom evidence UI
- Parallel analysis comparisons

**CopilotKit Integration:**
- Provides in-context AI assistance for analysts
- Allows AI to suggest next steps
- Supports custom "copilot actions" for tool integration
- Evidence UI can request AI help on demand
- Maintains chat context while staying in analysis flow

**Stack:**
- React 19
- Vite (dev server on 5173)
- TailwindCSS + Radix UI components
- CopilotKit `@copilotkit/react-core` + `@copilotkit/react-ui`
- Wouter for routing

### Routing Decision

```
User accesses app
  ├─→ HTTPS on localhost:443
  │   └─ Caddy routes to appropriate service
  │
  ├─→ /chat/* → DIAL Chat (port 3000)
  │   └─ Official DIAL for dev/admin
  │
  └─→ / (root) → Custom React App (port 5173)
      └─ HITL evidence analysis interface
```

---

## Key Design Principles

1. **Atomic Tools**
   Each MCP tool does ONE thing well. Composition happens at DIAL orchestration level.

2. **Lazy Loading**
   Heavy dependencies (models, databases) initialized on first use, not startup.

3. **External LLMs Only**
   All inference via hosted APIs (OpenRouter, OpenAI, Azure, Anthropic). No local GPU required, reduces ops burden.

4. **Spec-Driven Development**
   No code without a documented plan (see `SPEC_DRIVEN_DEVELOPMENT.md`). Specs define tool signatures, data schemas, API contracts.

5. **Chain of Custody**
   - SHA-256 fingerprint at first touch
   - UUIDv7 assignment
   - WORM (Write-Once-Read-Many) Pass 1
   - Full provenance recorded in Neo4j (PROV-O)

6. **Dual Retrieval**
   - WunderGraph for deterministic, auditable queries
   - DIAL native for ad-hoc exploration
   - Queries promoted from native → federation based on usage

7. **HITL via CopilotKit**
   - Analysts drive analysis
   - AI provides context-aware suggestions
   - Evidence tagged and reviewed by humans
   - AI learns from corrections

---

## Component Details

### WunderGraph Cosmo

Located at `/dial-stack/infrastructure/interceptors/` (planned).

**Role:** GraphQL federation gateway

**Responsibilities:**
- Accept GraphQL queries
- Route sub-queries to multiple backends (PostgreSQL, Neo4j, LanceDB)
- Merge results
- Log audit trail
- Apply access control

**Deployment:**
```yaml
service: cosmo
image: cosmo-router  # WunderGraph Cosmo image
port: 4000
environment:
  - GRAPHQL_SCHEMA=/etc/cosmo/schema.graphql
  - BACKENDS=postgres://...,neo4j://...
```

### MCP Servers

Each server is a **self-contained microservice** running independently.

#### TS MCP Server (8081)

**Technology:** Node.js + TypeScript + Express

**Tools:**
- `parse_sms_xml` — Extract SMS conversations
- `parse_facebook_json` — Extract Facebook messages
- `parse_whatsapp_txt` — Parse WhatsApp exports
- `parse_pdf_imessage` — Extract iMessage PDFs
- `detect_format` — Identify file type
- `fingerprint_file` — SHA-256 + metadata
- `write_evidence` — Insert into PostgreSQL

**Database Access:**
- PostgreSQL (write evidence records)
- DuckDB (read/write fingerprints, dedup state)

#### Py MCP Server (8082)

**Technology:** Python + FastAPI

**Tools:**
- `extract_entities` — Named Entity Recognition (Semantica)
- `build_graph` — Create temporal KG (Neo4j)
- `semantic_search` — Vector similarity (LanceDB)
- `cypher_query` — Execute Neo4j graph traversals
- `extract_temporal_facts` — Identify events + dates

**Database Access:**
- Neo4j (read/write graph)
- LanceDB (write embeddings, read vectors)
- PostgreSQL (read evidence for analysis)

#### JS MCP Server (8083)

**Technology:** Node.js + JavaScript + Express

**Tools:**
- `transform_text` — Text manipulation utilities
- `extract_regex` — Pattern matching
- `format_json` — JSON transformation
- `call_external_api` — HTTP adapter
- Custom logic hooks

**Database Access:**
- None (stateless, pure logic)

### Semantica NLP Engine

Remains the **primary NLP backbone** for:
- Entity extraction (people, places, organizations, dates)
- Entity linking (resolving duplicate mentions)
- Relationship extraction
- Graph construction
- Temporal reasoning

**Integration Points:**
- Invoked by Py MCP Server
- Results stored in Neo4j + PostgreSQL
- Embeddings sent to LanceDB

---

## Environment Variables

### Mandatory

```bash
# OpenRouter API key (multi-model router)
OPENROUTER_API_KEY=sk-or-v1-...

# PostgreSQL credentials
POSTGRES_USER=dial
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=evidence
DATABASE_URL=postgresql://dial:your_password@postgres:5432/evidence

# Keycloak credentials
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your_admin_password
```

### Optional (with Defaults)

```bash
# Neo4j (Tier 3)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# LanceDB (Tier 2)
LANCEDB_PATH=./data/lancedb/multimodal_vault

# DuckDB (Tier 1)
DUCKDB_PATH=./data/duckdb/forensic_vault.db

# Semantica NLP models
SEMANTICA_NER_MODEL=en_core_web_sm
SEMANTICA_EMBEDDING_MODEL=all-MiniLM-L6-v2
SEMANTICA_CONFIDENCE_THRESHOLD=0.7

# Cloudflare R2 (object storage for large binaries)
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=dial-storage
```

---

## Key Changes from Legacy (MCP_Tool_Platform)

| Component | Legacy | Current | Reason |
|-----------|--------|---------|--------|
| **GraphQL** | WunderGraph deprecated | WunderGraph Cosmo added back | Deterministic, auditable retrieval required |
| **Frontend** | DIAL Chat only | DIAL Chat + Custom React + CopilotKit | HITL analyst workflows + in-context AI |
| **Auth** | None in legacy | Keycloak OIDC | Enterprise auth, multi-user support |
| **LLM** | Local + API mixing | External APIs only (OpenRouter) | Simpler ops, cost transparency, no GPU |
| **ORM** | LangChain | Native MCP + DIAL orchestration | Lighter, faster, more explicit control |
| **Databases** | 5 tiers (MySQL Tier 5) | 4 tiers (consolidated) | Reduced complexity, single ACID store |
| **Knowledge Graph** | Graphiti legacy | Semantica + Neo4j | Modern NLP, cleaner architecture |
| **Retrieval** | Single path (tool calls) | Dual retrieval (WG + DIAL native) | Balance between audit and exploration |
| **Reverse Proxy** | nginx | Caddy | Simpler config, automatic HTTPS |
| **Cache** | Redis | Dragonfly | Drop-in Redis replacement, better perf |

---

## Deployment

### Local Development

```bash
# Start the full stack
docker-compose up -d

# Access services
DIAL Chat:  http://localhost:3000
Custom App: http://localhost:5173
DIAL Core:  http://localhost:8080
Keycloak:   http://localhost:8180
```

### Production (Kubernetes / Cloud)

- Containerize each service
- Use StatefulSets for databases
- Ingress controller for Caddy replacement
- Persistent volumes for DuckDB, LanceDB, PostgreSQL
- Secrets manager for API keys

---

## Debugging & Observability

### Logs

```bash
# DIAL Core logs
docker-compose logs -f core

# MCP Server logs
docker-compose logs -f ts-mcp-server
docker-compose logs -f py-mcp-server
docker-compose logs -f js-mcp-server

# Keycloak logs
docker-compose logs -f keycloak
```

### Database Inspection

```bash
# PostgreSQL
psql postgresql://dial:password@localhost:5432/evidence

# Neo4j Browser
http://localhost:7687

# DuckDB CLI
duckdb ./data/duckdb/forensic_vault.db

# LanceDB Python
python -c "import lancedb; db = lancedb.connect('./data/lancedb'); print(db.table_names())"
```

### Performance Monitoring

- **Dragonfly** (Redis): Monitor cache hit rate
- **PostgreSQL**: Query explain plans, slow log
- **Neo4j**: Graph stats, query profiling
- **WunderGraph Cosmo**: GraphQL query logs
- **DIAL Core**: Request latency, tool call counts

---

## Related Documentation

- **Spec-Driven Development:** `docs/SPEC_DRIVEN_DEVELOPMENT.md`
- **Tool Catalog:** `docs/TOOL_CATALOG.md`
- **Data Sources:** `docs/DATA_SOURCES.md`
- **Architecture Decisions:** `docs/adr/`
- **Roadmap:** `docs/ROADMAP.md`

---

## Version History

- **v2.0** (2026-03-12): Added WunderGraph Cosmo, CopilotKit, Keycloak, dual retrieval, custom React frontend, consolidated MySQL into PostgreSQL
- **v1.0** (2026-03-01): Initial architecture with TS/Py/JS MCP servers, 5 storage tiers, DIAL Chat
