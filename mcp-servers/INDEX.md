# MCP Servers Layer — Agent Index
> Read parent INDEX.md before this one.
> Check local TODO.md for approved tasks before starting work.

---


## I need to know cross-server coordination rules
→ `AGENTS.md` — MCP layer rules
→ `TODO.md` — cross-server tasks

## I need to work on a specific server
→ `ts-mcp-server/` — parsers, DuckDB, PostgreSQL, review queue
→ `py-mcp-server/` — Semantica, LanceDB, Neo4j, document intelligence
→ `js-mcp-server/` — text utilities

## I need to know the state of each server
→ `ts-mcp-server/memory/MEMORY.md`
→ `py-mcp-server/memory/MEMORY.md`
→ `js-mcp-server/memory/MEMORY.md`

## I need tool documentation
→ `docs/wiki/tools/INDEX.md` — all registered MCP tools

## Server ports
| Server | Port | Owns |
|--------|------|------|
| ts-mcp-server | 8081 | Parsers, DuckDB vault, PostgreSQL writes, Review Queue |
| py-mcp-server | 8082 | Semantica NLP, LanceDB, Neo4j, Document Intelligence |
| js-mcp-server | 8083 | Text utilities, format handlers |
