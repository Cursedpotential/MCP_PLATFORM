---
title: Py MCP Server
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# Py MCP Server

## Overview

The Python MCP server exposes 26 live tools through FastMCP. It combines Semantica, graph and vector access, DPK-derived analysis, voice fingerprinting, placeholder user-detection tools, and workflow orchestration.

Sources: `mcp-servers/py-mcp-server/src/server.py`

## Tool Groups

### Semantica and Provenance

- `semantica_extract_entities`
- `semantica_build_graph`
- `semantica_extract_temporal_facts`
- `semantica_detect_conflicts`
- `semantica_generate_embeddings`
- `semantica_track_provenance`

Sources: `mcp-servers/py-mcp-server/src/server.py`

### LanceDB

- `lancedb_vector_search`
- `lancedb_upsert`
- `lancedb_list_collections`

Sources: `mcp-servers/py-mcp-server/src/server.py`

### Neo4j

- `neo4j_cypher_query`
- `neo4j_get_entity_timeline`

Sources: `mcp-servers/py-mcp-server/src/server.py`

### DPK and Text Analysis

- `dpk_hap_score`
- `dpk_pii_redact`
- `dpk_lang_id`
- `dpk_doc_quality`
- `dpk_readability`
- `fingerprint_voice`

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/dpk_tools.py`, `mcp-servers/py-mcp-server/src/tools/voice_tools.py`

### User Detection

- `user_behavioral_detection`
- `user_darvo_detection`
- `user_coercive_control`

These are exposed, but the underlying module still describes them as placeholders or adapters for user-specific systems.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/user_detection.py`

### Workflow Engine

- `workflow_list`
- `workflow_run`
- `workflow_update_config`
- `workflow_add_module`
- `workflow_remove_module`

Workflow composition is driven by `config/workflows.json`.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/config/workflows.json`, `mcp-servers/py-mcp-server/src/tools/workflow_tools.py`

### Health

- `ping`

Sources: `mcp-servers/py-mcp-server/src/server.py`

## Architecture Notes

- The server uses lazy initialization for Neo4j, LanceDB, NER, graph builder, temporal query, conflict detection, embeddings, and provenance.
- Some additional helper modules exist in `src/tools/` for hashing, evidence signing, WAL parsing, and auditing, but they are not currently registered as MCP tools in `server.py`.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/hash_verification.py`, `mcp-servers/py-mcp-server/src/tools/evidence_signing.py`, `mcp-servers/py-mcp-server/src/tools/sqlite_wal_parser.py`, `mcp-servers/py-mcp-server/src/tools/audit_hooks.py`

## Known Gaps

- The user-detection tools need clearer backing implementations if they are meant to be production-grade.
- Real end-to-end validation against evidence data is still missing from the live docs and manifests.
- Not every useful helper in `src/tools/` is exposed as an MCP endpoint yet.

Sources: `mcp-servers/py-mcp-server/src/tools/user_detection.py`, `docs/plans/ROADMAP.md`

## Change Log

- 2026-04-08, rev 2, Codex: corrected the tool count and aligned the page to the actual registered FastMCP surface.
