---
title: TS MCP Server
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# TS MCP Server

## Overview

The TypeScript MCP server exposes 18 live tools over HTTP. It handles parser entrypoints, DuckDB vault actions, PostgreSQL access, provider and prompt administration, and HITL review queue operations.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`

## Tool Groups

### Parsers

- `parse_sms_xml`
- `parse_facebook_export`
- `parse_imessage_pdf`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/SmsXmlParser.ts`, `mcp-servers/ts-mcp-server/src/tools/FacebookExportParser.ts`, `mcp-servers/ts-mcp-server/src/tools/ImessagePdfParser.ts`

### Vault and Storage

- `vault_log_ingestion`
- `vault_get_pending_pass1`
- `vault_update_pass1_status`
- `vault_update_write_tracking`
- `postgres_write_record`
- `postgres_raw_query`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/DuckDbVault.ts`, `mcp-servers/ts-mcp-server/src/tools/PostgresWriter.ts`

### Administration

- `admin_list_llm_providers`
- `admin_upsert_llm_provider`
- `admin_list_system_prompts`
- `admin_upsert_system_prompt`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/AdminTools.ts`

### Review Queue

- `review_list_pending`
- `review_approve`
- `review_reject`
- `review_submit`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/ReviewQueue.ts`

### Health

- `ping`

Sources: `mcp-servers/ts-mcp-server/src/index.ts`

## Architecture Notes

- The HTTP server is implemented with Express and `StreamableHTTPServerTransport`.
- Long-lived helper instances are wrapped behind `getVault`, `getPg`, `getAdmin`, and `getReview`.
- Tool invocation still dispatches through a `switch` statement rather than a registry.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`

## Known Gaps

- No DuckDB read/query tool is exposed.
- No format detector, WhatsApp parser, ChatGPT parser, or Google Timeline parser is registered here.
- `postgres_raw_query` remains a sensitive surface that deserves careful review.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `docs/plans/ROADMAP.md`

## Change Log

- 2026-04-08, rev 2, Codex: replaced the older narrative doc with an accurate live-tool summary.
