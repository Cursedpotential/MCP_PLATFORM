# AGENTS.md — mcp-servers/ts-mcp-server/

> Domain rules for the TypeScript MCP server. Read after `mcp-servers/AGENTS.md`.

## This server owns
Parsers, DuckDB vault, PostgreSQL writes, Pass-1 runner, review queue, chain of custody (pending port), evidence ingestor.

## Working tools (do NOT touch without approved task)
- `SmsXmlParser.ts` — working
- `SmsEvidenceIngestor.ts` — working
- `DuckDbVault.ts` — working
- `PostgresWriter.ts` — working
- `ReviewQueue.ts` — working
- `Pass1Runner.ts` — working
- `MessageChunker.ts` — working
- `EvidenceIngestor.ts` — working (SMS path only; FB/iMessage return unsupported_format)

## Stubs (port priority order — do not skip ahead)
1. `FacebookExportParser.ts` — STUB — port priority #1
2. `ImessagePdfParser.ts` — STUB — port priority #2
3. `ChainOfCustody.ts` — NOT YET PORTED — port priority #4

## Domain-specific rules
- SHA-256 at first touch. Every parser must hash the source file before any other operation.
- No direct PostgreSQL writes without going through `PostgresWriter`.
- No DuckDB writes without going through `DuckDbVault`.
- `Pass1Runner` calls py-mcp-server tools — treat those calls as non-fatal. Log failures. Continue.
- Before any change to a working tool: REQUIRES_CONFIRMATION + Step-Back Analysis.

## Read next
`ts-mcp-server/memory/MEMORY.md` → `ts-mcp-server/TODO.md` → `ts-mcp-server/INDEX.md`

*Last updated: 2026-04-21*
