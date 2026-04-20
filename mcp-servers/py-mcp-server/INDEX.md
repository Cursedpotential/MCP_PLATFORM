# Py MCP Server — Agent Index
> Read parent INDEX.md before this one.
> Check local TODO.md for approved tasks before starting work.

---


## I need to work on NLP / Semantica
→ `src/tools/` — check for semantica_tools.py (verify exists)
→ Alpha 1 source: `MCP_Tool_Platform/server/mcp/nlp/`
→ Docs: `docs/wiki/tools/nlp/semantica.md` (produced by docs agent)

## I need to work on embeddings / LanceDB
→ `src/tools/` — EmbeddingService (PLANNED — not yet implemented)
→ Blocked by OQ-5: embedding model selection pending

## I need to work on the document intelligence router
→ `src/document_intelligence/router.py` — EngineRouter interface
→ `src/document_intelligence/engines/` — all stubs, none active
→ Docs: `docs/wiki/tools/document-intelligence/overview.md`

## I need to work on HurtLex
→ Alpha 1 source: `MCP_Tool_Platform/server/mcp/nlp/`
→ Target: port to py-mcp-server

## I need to work on audit hooks
→ `src/tools/audit_hooks.py` — exists

## I need to check what's approved to work on
→ `TODO.md` — Py server task list

## I need to check last session state
→ `memory/MEMORY.md`

## Rules specific to this server
→ `AGENTS.md` — Py server local rules
→ `src/server.py` is the MCP registration surface
