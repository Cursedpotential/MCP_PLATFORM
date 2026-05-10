# AGENTS.md — mcp-servers/js-mcp-server/

> Domain rules for the JavaScript MCP server. Read after `mcp-servers/AGENTS.md`.

## This server owns
Text utilities, format handlers. Currently: ping tool only.

## Current state
One live tool: `ping`. Everything else is planned.

## Domain-specific rules
- This server is a stub. Do not expand it without an approved task naming the specific tool.
- If adding a tool: internal service class first, MCP registration last.
- Keep `index.js` clean — do not add business logic to the entry point.

## Read next
`js-mcp-server/memory/MEMORY.md` → `js-mcp-server/TODO.md` → `js-mcp-server/INDEX.md`

*Last updated: 2026-04-21*
