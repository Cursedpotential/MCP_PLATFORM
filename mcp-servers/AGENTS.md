# AGENTS.md — mcp-servers/

> Domain rules for ALL MCP servers. Read this after root AGENTS.md. Read the server-specific AGENTS.md after this.

## This domain owns
All three MCP server implementations: TS (8081), Py (8082), JS (8083).

## Rules specific to this domain

1. **Server boundaries are hard.** TS server does not call Py server directly — they communicate through internal APIs or Conductor task calls. No server imports another server's code.
2. **Tool registration is the last step.** Build the internal service class first. Wire the MCP tool registration last.
3. **No cross-server assumptions.** Do not assume the other server is running. Always handle `py-mcp-server unreachable` gracefully — non-fatal, log and continue.
4. **Alpha 1 first.** Before writing any new parser or NLP tool, search `MCP_Tool_Platform/server/mcp/` first.
5. **Semantica is authoritative.** Do not rewrite, stub, or work around Semantica tool interfaces. Flag and ask if broken.

## Conductor worker skill
When registering workers or wiring MCP tools into Conductor workflows, load:
`docs/wiki/skills/orchestration/conductor/SKILL.md`

Worker task type naming convention for this domain: `{server}.{domain}.{action}`
  - `ts.parse.facebook`, `ts.parse.imessage`, `ts.db.write_postgresql`
  - `py.nlp.semantica_extract`, `py.graph.build_knowledge_graph`, `py.vector.index_embeddings`
  - `js.legacy.*`

## Read next (cascade inward)
Working in TS server → `ts-mcp-server/AGENTS.md`
Working in Py server → `py-mcp-server/AGENTS.md`
Working in JS server → `js-mcp-server/AGENTS.md`

*Last updated: 2026-04-21*
