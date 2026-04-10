# ts-mcp-server (AI DIAL Stack)

## Architecture Overview
This directory contains the **TypeScript MCP Server**, which is designed specifically to interface with the **AI DIAL** orchestration framework. 

This is part of **Sprint 1** to replace the monolithic, over-engineered `production-pipeline.ts` and `coordinator.ts` found in the root `MCP_Tool_Platform`. AI DIAL Native handles all orchestration, execution graphs, and dynamic routing. **This server only registers atomic, independent tools**.

## Purpose & Scope
This server wraps lightweight, fast Node.js/TypeScript modules into MCP Tool endpoints.
Specifically, it is restricted to the following responsibilities (as defined in `mcp_extraction_blueprint.md`):

### 1. The Core Parsers
*   Facebook HTML Parser
*   SMS XML Extractors
*   WhatsApp TXT Modulo
*   iMessage PDF OCR module

### 2. The Core Relational Data Connectors
*   DuckDB analytical querying/inserts
*   PostgreSQL entity management

## AI Agent Handover Notes (Rate Limiting/New Sessions)
If you are a new agent taking over this project:
1.  **DO NOT REBUILD HARDCODED PIPELINES**. We are using AI DIAL. If you see a file trying to sequentially call `detectFormat -> parse -> embed -> ingest`, **delete it or ignore it**. Your job is to strictly expose tools for an LLM orchestrator to call dynamically.
2.  **Strict Isolation**. This `ts-mcp-server` subdirectory is completely pristine. **Do not** import from the fragmented "TraceIQ" directories (`D:\AI_Workspace\...`) in this subdirectory.
3.  **To Add a Tool**: Add a new module in `src/tools/` wrapping one of the legacy extractors from `../../server/mcp/ingest/formats/`, configure it as an MCP tool in `src/index.ts`, and restart the local DIAL stack.

## Getting Started
```bash
npm install
npm run build
npm start
```
