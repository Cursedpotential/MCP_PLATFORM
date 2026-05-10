# AGENTS.md — mcp-servers/py-mcp-server/

> Domain rules for the Python MCP server. Read after `mcp-servers/AGENTS.md`.

## This server owns
Semantica NLP pipeline, LanceDB vector operations, Neo4j graph operations, document intelligence engines, DPK tools, audit hooks, evidence signing, hash verification.

## Semantica — CRITICAL
Semantica is the forensic intelligence layer. Its tools are authoritative:
- `semantica_extract_entities` — NER
- `semantica_build_graph` — knowledge graph
- `semantica_extract_temporal_facts` — temporal analysis
- `semantica_detect_conflicts` — contradiction detection
- `semantica_generate_embeddings` — vector generation
- `semantica_track_provenance` — provenance chains

**Do NOT rewrite these interfaces. Do NOT stub these calls. If broken: emit `UNKNOWN_COMPONENT: semantica.[tool]` and stop.**

## Document intelligence engines
All 11 engines are stubs. Activation order (local-only first):
1. `pandoc_engine.py` — no cloud dependency
2. `tesseract_engine.py` — no cloud dependency
Everything else requires explicit owner approval naming the engine.

## Domain-specific rules
- `server.py` is the MCP registration surface. Not every tool in `src/tools/` is exposed.
- Do not activate cloud engines (AWS Textract, Google DocAI, IBM watsonx, LlamaParse) without `approved — proceed [engine name]`.
- LanceDB operations are non-fatal. Log and continue if LanceDB is unreachable.

## Read next
`py-mcp-server/memory/MEMORY.md` → `py-mcp-server/TODO.md` → `py-mcp-server/INDEX.md`

*Last updated: 2026-04-21*
