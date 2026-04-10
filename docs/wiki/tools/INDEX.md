---
title: MCP Server Index
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# MCP Server Index

## Overview

This index covers the MCP servers implemented in this repo, not external tool catalogs.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`

## Servers

- [TS MCP Server](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/ts-mcp-server.md): 18 live tools for parsers, vault/storage, admin, and review flows.
- [Py MCP Server](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/py-mcp-server.md): 26 live tools for Semantica, vectors, graph access, DPK, voice, user detection, and workflows.
- [JS MCP Server](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/js-mcp-server.md): 1 live health-check tool and placeholder space for future wrappers.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`

## Related Catalogs

- [Tools and Utilities Intake Catalog](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/INDEX.md): staged applications, vendored tools, extracted sources, scripts, and external MCP candidates stored under `tools/utilities/`.

Sources: `docs/wiki/tools/utilities/INDEX.md`

## Notes

- `docs/wiki/tools/semantica/` contains embedded Semantica material and tests; it is not the primary MCP server reference.
- If tool registration changes, update this index and the corresponding server page in the same change.

Sources: `docs/wiki/tools/semantica`, `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md`

## Change Log

- 2026-04-08, rev 2, Codex: replaced the stale external-tool catalog with the actual repo MCP server index.
