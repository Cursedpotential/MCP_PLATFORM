# TS MCP Server Instructions

- This server owns parser entrypoints, DuckDB vault operations, PostgreSQL access, admin tools, and review queue tools.
- Preserve the HTTP MCP transport and the lazy singleton wrappers in `src/index.ts`.
- Keep tool documentation aligned with `docs/wiki/tools/ts-mcp-server.md`.
