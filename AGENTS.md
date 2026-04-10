# AI DIAL Stack — Multi-Agent Orchestration Guide

**Project**: AI DIAL MCP Tool Stack
**Type**: Forensic evidence processing platform with federated MCP tool servers
**Architecture**: AI DIAL Gateway + 3 MCP Servers (TS, Python, JS)

> This is the root instruction file. Deeper `AGENTS.md` files add narrower, local context for their subtree and should be preferred when working inside that directory.

---

## Agent Roles

This project uses specialized agent roles for different concerns:

### Storage Agent
**Focus**: DuckDB, PostgreSQL, LanceDB, Neo4j tier interactions
**Files**: `mcp-servers/ts-mcp-server/src/services/`, `mcp-servers/py-mcp-server/src/services/`
**Patterns**:
- DuckDB for SHA-256 fingerprinting, UUIDv7, dedup, master clock
- PostgreSQL for normalized evidence and app data
- LanceDB for vector embeddings
- Neo4j for temporal knowledge graph (via Semantica)
- Always use lazy initialization for database connections

### Parser Agent
**Focus**: Document parsing, format detection, evidence ingestion
**Files**: `mcp-servers/ts-mcp-server/src/tools/*Parser.ts`
**Patterns**:
- Each parser wraps a legacy loader from `MCP_Tool_Platform/server/mcp/loaders/`
- Parsers output normalized `EvidenceBatch` with confidence scores
- Format detection before parsing, validation after

### NLP Agent
**Focus**: Semantica pipeline, entity extraction, graph building
**Files**: `mcp-servers/py-mcp-server/src/semantica_tools.py`
**Patterns**:
- NER extraction → Neo4j nodes
- Relation extraction → Neo4j edges
- Temporal facts → valid_from/valid_to properties
- W3C PROV-O for provenance chains

### Enrichment Agent
**Focus**: Two-pass classification (blind + hindsight)
**Files**: `mcp-servers/py-mcp-server/src/enrichment_tools.py` (planned)
**Patterns**:
- Pass 1: 24-hour context window, sentiment, intent, entities (WORM)
- Pass 2: Full longitudinal context, contradiction detection, gaslighting patterns

### Infrastructure Agent
**Focus**: Docker, docker-compose, Keycloak, WunderGraph Cosmo
**Files**: `infrastructure/`, `docker-compose.yml`
**Patterns**:
- All services run in containers
- Keycloak for OIDC/JWT authentication
- WunderGraph Cosmo for GraphQL federation
- Caddy for HTTPS termination and routing

---

## Agent Communication Patterns

### Tool Dispatch Flow
```
User Query → AI DIAL Core → MCP Tool Dispatch
                              ├── TS MCP Server (parsers, storage)
                              ├── Py MCP Server (NLP, graph)
                              └── JS MCP Server (utilities)
                                        ↓
                           Storage Tier Write (DuckDB → PostgreSQL → LanceDB/Neo4j)
```

### Dual Retrieval Pattern
```
User Query → DIAL Core Decision Engine
              ├── Known WunderGraph operation?
              │   └── YES → Route to Cosmo (audited, deterministic)
              └── Ad-hoc exploratory?
                  └── YES → Native tool call (flexible, not audited)
```

---

## Coordination Rules

1. **Never bypass the Coordinator** — All evidence operations flow through the coordinator pattern, not direct database access
2. **Respect tier boundaries** — DuckDB for fingerprints, PostgreSQL for relations, LanceDB for vectors, Neo4j for graph
3. **Chain of custody** — SHA-256 at first touch, immutable Pass 1
4. **Spec-first development** — All code changes must have a documented plan in `docs/specs/`
5. **Read-only legacy** — Never modify files in `MCP_Tool_Platform/`

---

## Documentation Rules

1. **Start with `docs/INDEX.md`** — It is the entrypoint to the live documentation tree.
2. **Keep live docs in `docs/`** — Architecture, roadmap, guides, specs, and wiki pages are current only when they live in the active docs tree.
3. **Archive by mirrored path** — Superseded docs move to `docs/archive/<same-relative-path>`.
4. **Treat `docs/wiki/.plannotator/` as planning history** — `.plannotator` is a compatibility symlink, not the primary docs system of record.
5. **Keep repo sidecar workspaces under `docs/wiki/`** — `.annotative`, `.full-review`, `.planning`, and `.redline` resolve there from the repo root.

---

## Local Environment Notes

1. **Canonical GitHub SSH identity for this workstation is the WSL key** — Use `/home/matts/.ssh/id_ed25519` when pushing from the repo in WSL.
2. **Do not assume Windows Git has the active key material** — `C:\Users\matts\.ssh` may only contain host trust files unless explicitly synchronized.
3. **Before any GitHub push, verify auth with WSL first** — Run `GIT_SSH_COMMAND="ssh -i /home/matts/.ssh/id_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes" git ls-remote origin -h refs/heads/main` before attempting a push.
4. **Before any large docs push, run the local pre-push secret scan** — Use `scripts/git/prepush-check.sh` to catch obvious secrets and notebook outputs before GitHub push protection rejects the upload.
5. **Do not debug pushes through Windows Git first on this machine** — Default to WSL Git for fetch/push operations unless the repo is being intentionally migrated.

---

## MCP Server Ports

| Server | Port | Purpose |
|--------|------|---------|
| TS MCP | 8081 | Parsers, DuckDB, PostgreSQL writes |
| Py MCP | 8082 | Semantica, LanceDB, Neo4j operations |
| JS MCP | 8083 | Text utilities, format handlers |

## Storage Tier Ports

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Evidence + app data |
| Neo4j | 7687 | Knowledge graph |
| DuckDB | — | Embedded (file-based) |
| LanceDB | — | Embedded (file-based) |

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| DIAL Core | 8080 | API gateway |
| DIAL Chat | 3000 | Dev/admin UI |
| React + CopilotKit | 3002/5173 | HITL evidence review |
| Keycloak | 8180 | OIDC provider |
| WunderGraph Cosmo | 4000 | GraphQL federation |

---

## Current Development Phase

**Phase A: Foundation & Storage Tools** (~70% complete)

See `docs/plans/ROADMAP.md` for detailed progress tracking.

---

**Last Updated:** March 17, 2026
