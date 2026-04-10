# Py MCP Server Instructions

- This server owns Semantica, LanceDB, Neo4j, DPK analysis, workflow execution, and related helper modules.
- `src/server.py` is the MCP registration surface; not every helper in `src/tools/` is exposed automatically.
- Keep tool counts and capability docs aligned with `docs/wiki/tools/py-mcp-server.md`.
