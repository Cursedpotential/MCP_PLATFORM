# TS MCP Server — Agent Index
> Read parent INDEX.md before this one.
> Check local TODO.md for approved tasks before starting work.

---


## I need to work on parsers
→ `src/tools/SmsXmlParser.ts` — SMS XML (WORKING — do not modify without approval)
→ `src/tools/FacebookExportParser.ts` — Facebook JSON (STUB — needs Alpha 1 port)
→ `src/tools/ImessagePdfParser.ts` — iMessage (STUB — needs Alpha 1 port)
→ Alpha 1 source: `MCP_Tool_Platform/server/mcp/loaders/`

## I need to work on storage
→ `src/tools/DuckDbVault.ts` — T1 first touch, SHA-256, UUIDv7
→ `src/tools/PostgresWriter.ts` — T4 normalized evidence writes
→ `src/services/DuckDbService.ts` — DuckDB connection service

## I need to work on the HITL review queue
→ `src/tools/ReviewQueue.ts` — approve/reject logic (PORTED — working)

## I need to work on evidence ingestion routing
→ `src/tools/EvidenceIngestor.ts` — format detection + parser routing

## I need to work on Pass 1 analysis
→ `src/tools/Pass1Runner.ts` — verify completeness before modifying

## I need to understand the messaging schemas
→ `docs/wiki/alpha1-inventory.md` → Section 2: Schema Inventory
→ Alpha 1 source: `MCP_Tool_Platform/server/mcp/loaders/production-message-schemas.ts`

## I need to check what's approved to work on
→ `TODO.md` — TS server task list

## I need to check last session state
→ `memory/MEMORY.md`

## Rules specific to this server
→ `AGENTS.md` — TS server local rules
