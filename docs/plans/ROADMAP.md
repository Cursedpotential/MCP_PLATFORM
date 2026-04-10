---
title: Development Roadmap
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# AI DIAL Stack Roadmap

## Overview

This roadmap is the live status view for the current repo. It distinguishes between what is checked in now, what is partially scaffolded, and what remains planned.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`, `client/src/App.tsx`

## Phase A: Core Runtime and Storage

Status: in progress

- Done: DIAL core configuration, Docker Compose stack, PostgreSQL init scripts, TS MCP server HTTP transport, DuckDB vault tool, PostgreSQL writer, admin tools, review queue, lazy singleton wrappers in TS MCP.
- Remaining: a dedicated DuckDB read/query tool, a composed DuckDB-to-PostgreSQL ingestion flow, and replacement of the TS `switch` dispatch with a registry pattern.

Sources: `docker-compose.yml`, `infrastructure/core/config.json`, `mcp-servers/ts-mcp-server/src/index.ts`

## Phase B: Parser Coverage

Status: in progress

- Done: SMS XML parsing, Facebook export parsing, iMessage PDF parsing.
- Remaining: WhatsApp TXT, ChatGPT export, Google Timeline, format detection, and archive extraction.

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/SmsXmlParser.ts`, `mcp-servers/ts-mcp-server/src/tools/FacebookExportParser.ts`, `mcp-servers/ts-mcp-server/src/tools/ImessagePdfParser.ts`

## Phase C: Semantic and Identification Tooling

Status: in progress

- Done: 26 Python MCP tools exposed through `server.py`, covering Semantica extraction, provenance, Neo4j queries, LanceDB operations, DPK pre-processing, voice fingerprinting, user-detection placeholders, and workflow execution.
- Remaining: end-to-end validation on real evidence and promotion of additional helper modules in `mcp-servers/py-mcp-server/src/tools/` where appropriate.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/dpk_tools.py`, `mcp-servers/py-mcp-server/src/tools/workflow_tools.py`, `mcp-servers/py-mcp-server/src/tools/voice_tools.py`, `mcp-servers/py-mcp-server/src/tools/user_detection.py`

## Phase D: Security and Routing Hardening

Status: in progress

- Done: Keycloak service is present in Compose, DIAL settings include JWT verification config, role/key configuration exists in `config.json`, and Caddy fronts the stack.
- Remaining: verify the auth flow end to end, tighten the proxy toward real HTTPS deployment, and resolve any stale model or routing entries such as local-only placeholders that contradict project policy.

Sources: `docker-compose.yml`, `infrastructure/settings/settings.json`, `infrastructure/core/config.json`, `infrastructure/Caddyfile`

## Phase E: Frontend and Analyst Experience

Status: early scaffold

- Done: a Vite/React app exists with CopilotKit and Radix dependencies installed.
- Remaining: replace the starter UI with the actual analyst workflow, connect it to DIAL/auth, and implement review/timeline/entity-resolution surfaces.

Sources: `client/package.json`, `client/src/App.tsx`, `client/src/main.tsx`

## Phase F: Federation and Advanced Platform Features

Status: planned

- WunderGraph Cosmo federation is still planned rather than implemented in the checked-in stack.
- More advanced forensic workflows such as hindsight analysis, contradiction packaging, and legal evidence assembly remain planned.

Sources: `docs/architecture/ARCHITECTURE.md`, `docs/archive/plans/IMPLEMENTATION_HANDOFF.md`

## Notes on Historical Planning

Historical requirement and plan material still exists under `docs/wiki/.plannotator/` and other recovered planning folders, but this roadmap is the live status page.

Sources: `docs/references/PLANNOTATOR.md`

## Change Log

- 2026-04-08, rev 2, Codex: rewrote the roadmap to reflect the checked-in codebase instead of older aspirational phase claims.
