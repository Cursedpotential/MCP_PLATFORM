---
title: Development Guide
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Development Guide

## Overview

`dial-stack` is a multi-service repo centered on AI DIAL, three MCP servers, PostgreSQL, and a partially scaffolded React client. The checked-in code supports local service orchestration with Docker Compose and direct subproject development inside `client/` and `mcp-servers/`.

Sources: `docker-compose.yml`, `client/package.json`, `mcp-servers/ts-mcp-server/package.json`, `mcp-servers/py-mcp-server/requirements.txt`, `mcp-servers/js-mcp-server/package.json`

## Tech Stack

- AI DIAL core, chat, themes, auth-helper, analytics, and realtime services run in `docker-compose.yml`.
- The TypeScript MCP server uses Express plus the MCP SDK.
- The Python MCP server uses FastMCP, Semantica, Neo4j, LanceDB, and additional analysis helpers.
- The JavaScript MCP server is a minimal MCP HTTP wrapper with one live tool.
- The frontend is a Vite + React 19 scaffold with CopilotKit and Radix dependencies installed but not yet integrated into a production analyst UI.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`, `client/package.json`, `client/src/App.tsx`

## Environment Setup

1. Copy `.env.example.bak` or your preferred environment template into a working `.env`.
2. Set at least `OPENROUTER_API_KEY`, `POSTGRES_PASSWORD`, and the Keycloak variables used by `docker-compose.yml`.
3. Start the stack from the repo root with `docker compose up -d --build`.
4. For focused local development, use the per-project scripts:
   - `client`: `npm install`, `npm run dev`
   - `mcp-servers/ts-mcp-server`: `npm install`, `npm run dev`
   - `mcp-servers/py-mcp-server`: create a virtual environment, `pip install -r requirements.txt`, then run `python src/server.py` or `fastmcp run src/server.py`
   - `mcp-servers/js-mcp-server`: `npm install`, `npm start`

Sources: `README.md`, `docker-compose.yml`, `client/package.json`, `mcp-servers/ts-mcp-server/package.json`, `mcp-servers/py-mcp-server/README.md`, `mcp-servers/js-mcp-server/package.json`

## Repository Structure

- `infrastructure/`: DIAL settings, model config, Caddy, init SQL, and audit logger code.
- `mcp-servers/`: TS, Python, and JS MCP server implementations.
- `client/`: React frontend scaffold.
- `docs/`: live docs, archive, wiki, references, and specs.
- `docs/wiki/.plannotator/`: the relocated planning workspace; `.plannotator` is a compatibility symlink.
- `docs/wiki/.annotative/`, `docs/wiki/.full-review/`, `docs/wiki/.planning/`, and `docs/wiki/.redline/`: repo sidecar workspaces moved under the documentation tree.

Sources: `docker-compose.yml`, `infrastructure/core/config.json`, `docs/references/PLANNOTATOR.md`

## Workflow

1. Read `docs/INDEX.md`, `docs/architecture/ARCHITECTURE.md`, and `docs/plans/ROADMAP.md`.
2. If you are changing behavior, write or update a spec in `docs/specs/` before editing code.
3. Keep architecture claims honest. Mark planned work as planned instead of describing it as shipped.
4. Update the matching wiki or roadmap page after significant implementation changes.
5. Archive superseded docs under the mirrored path in `docs/archive/`.

Sources: `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md`, `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Verification

- Frontend: `npm run build` in `client/`
- TS MCP server: `npm run build` in `mcp-servers/ts-mcp-server/`
- Python MCP server: no single canonical test command is documented in the checked-in files; verify imports and targeted flows manually or add explicit tests when touching behavior.
- Full stack: `docker compose config` and focused container runs via `docker compose up`

Sources: `client/package.json`, `mcp-servers/ts-mcp-server/package.json`, `mcp-servers/py-mcp-server/README.md`, `docker-compose.yml`

## Change Log

- 2026-04-08, rev 1, Codex: created a live development guide aligned to the checked-in manifests and current repo layout.
