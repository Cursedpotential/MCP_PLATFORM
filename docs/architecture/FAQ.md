---
title: Architecture FAQ
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# FAQ

## What is the current live architecture?

- AI DIAL core plus chat and themes services.
- Three MCP servers: TypeScript, Python, JavaScript.
- PostgreSQL, LanceDB, Neo4j, Dragonfly, and supporting services in Docker Compose.
- See [Architecture](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/ARCHITECTURE.md).

Sources: `docker-compose.yml`, `docs/architecture/ARCHITECTURE.md`

## Is the React frontend production-ready?

- No.
- The repo contains a Vite starter-style app with CopilotKit and UI dependencies installed.
- The analyst UI described in older planning docs is still largely planned.
- See [Development Guide](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/guides/DEVELOPMENT.md) and [Roadmap](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/plans/ROADMAP.md).

Sources: `client/src/App.tsx`, `client/package.json`, `docs/plans/ROADMAP.md`

## Are all planned MCP tools implemented?

- No.
- TS MCP currently exposes 18 tools.
- Python MCP currently exposes 26 tools.
- JS MCP currently exposes 1 tool and remains mostly placeholder.
- See [Wiki Home](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/INDEX.md).

Sources: `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`, `docs/wiki/INDEX.md`

## Where did the old handoff and rough planning docs go?

- Superseded files are being moved into `docs/archive/` under mirrored paths.
- Dated references and audits remain under `docs/references/` and `docs/.audit/`.
- See [Documentation Index](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/INDEX.md) and [Archive Policy](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/archive/README.md).

Sources: `docs/INDEX.md`, `docs/archive/README.md`

## What is `plannotator` now?

- The real workspace now lives at `docs/wiki/plannotator/`.
- `.plannotator` is a compatibility symlink that points there.
- Treat it as planning history and workflow support, not the live documentation system of record.
- See [Plannotator Reference](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/references/PLANNOTATOR.md).

Sources: `.plannotator`, `docs/wiki/plannotator`, `docs/references/PLANNOTATOR.md`

## Change Log

- 2026-04-08, rev 1, Codex: created a short FAQ tied to the reorganized docs tree.
