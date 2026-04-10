# AI DIAL MCP Application Stack

This is the standalone application architecture designed to replace the legacy `MCP_Tool_Platform` rigid orchestrator.

> **Architectural Rule:** This repository (`dial-stack`) lives completely isolated from the legacy `MCP_Tool_Platform`. The legacy repo is archived and read-only — we only copy tools and patterns from it into this new stack.

## Architecture

The DIAL stack runs a federated network of language-specific Model Context Protocol (MCP) servers, orchestrated by the AI DIAL framework.

### Core Components

| Component | Description |
| --- | --- |
| `infrastructure/core/` & `infrastructure/settings/` | AI DIAL Gateway router definitions and configuration |
| `mcp-servers/ts-mcp-server/` | TypeScript MCP server: parsers, DuckDB forensic vault, PostgreSQL writer, admin tools, review queue |
| `mcp-servers/py-mcp-server/` | Python MCP server: Semantica NLP pipeline, Neo4j graphs, LanceDB vector embeddings (11 tools) |
| `mcp-servers/js-mcp-server/` | JavaScript MCP server: Pandoc/Docling wrappers (scaffolding) |

### Databases

| Database | Purpose | Hosting |
| --- | --- | --- |
| **PostgreSQL** (pgvector) | Relational storage for evidence + app data (consolidated from legacy MySQL) | Local Docker |
| **Neo4j** | Semantic and temporal knowledge graphs | Hosted (AuraDB free tier) |
| **DuckDB** | Forensic vault — SHA-256 hashing, write tracking, chain of custody | Embedded (in mcp-servers/ts-mcp-server) |
| **LanceDB** | Vector embeddings for semantic search | Local Docker volume |
| **Dragonfly** (Redis) | Session cache for DIAL Core | Local Docker |

### Security

- **Caddy** reverse proxy with HTTPS termination
- **Keycloak & AI DIAL Auth Helper** for strict OIDC/JWT authentication
- **Multi-key API roles**: admin, default, readonly
- Cryptographically auditable HITL review actions

## Getting Started

1. Copy `.env.example` to `.env` and set your variables:

   ```bash
   # Required
   OPENROUTER_API_KEY=your_key
   POSTGRES_PASSWORD=your_password

   # Keycloak Admin Credentials
   KEYCLOAK_ADMIN=admin
   KEYCLOAK_ADMIN_PASSWORD=admin_password

   # Hosted Neo4j
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   NEO4J_DATABASE=neo4j
   ```

2. Start the stack:

   ```bash
   docker compose up -d --build
   ```

3. Access the AI DIAL Chat UI at `http://localhost:3000`
4. Access Keycloak Admin Console at `http://localhost:8080/auth/`

## MCP Tools

### TypeScript Server (port 8081)

- `parse_sms_xml` — Parse Android SMS Backup XML
- `parse_facebook_export` — Parse Facebook Messenger HTML exports
- `vault_log_ingestion` — DuckDB forensic chain of custody with SHA-256
- `vault_update_write_tracking` — Track which tier has which data
- `postgres_write_record` — Write to PostgreSQL tables
- `admin_list_llm_providers` / `admin_upsert_llm_provider` — Manage LLM configs
- `admin_list_system_prompts` / `admin_upsert_system_prompt` — Manage prompts
- `review_list_pending` / `review_approve` / `review_reject` / `review_submit` — HITL review queue

### Python Server (port 8082)

- `semantica_extract_entities` — NER + relationship extraction
- `semantica_build_graph` — Neo4j knowledge graph construction
- `semantica_generate_embeddings` — LanceDB vector embeddings
- `semantica_query_graph` — Query the semantic graph
- Plus 7 more Semantica tools

### Agents

- **evidence-ingestion-agent** — Orchestrates full ingestion: parse → hash → store → enrich → audit
