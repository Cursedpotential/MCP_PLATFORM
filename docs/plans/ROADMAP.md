---
title: Development Roadmap
reviewed: 2026-04-11
revision: 3
author: Copilot
status: current
---

# AI DIAL Stack Roadmap

## Overview

This roadmap is the live status view for the current repo. It distinguishes between what is checked in now, what is partially scaffolded, and what remains planned.

Sources: `docker-compose.yml`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/js-mcp-server/src/index.js`, `client/src/App.tsx`

## Phase 0: Foundation Audit

Status: in progress

- Done: Phase 0 audit initiated; TypeScript build errors fixed; Directus service definition reviewed; asset inventory written to `docs/specs/alpha1-inventory.md`.
- Blocked: `MCP_Tool_Platform/` (Alpha 1) not present in this clone — cannot audit Alpha 1 source files or confirm `production-message-schemas.ts`. Owner decision required on how to provide Alpha 1 access.
- Remaining: runtime health verification of all services; test framework selection; Neo4j service definition; owner approval to proceed to Phase 1.

Sources: `docs/specs/alpha1-inventory.md`, `IMPLEMENTATION_PHASE_PLAN.md`

## Phase A: Core Runtime and Storage

Status: substantially complete

- Done: DIAL core configuration, Docker Compose stack, PostgreSQL init scripts, TS MCP server HTTP transport, DuckDB vault tool, PostgreSQL writer, admin tools, review queue, lazy singleton wrappers in TS MCP.
- Added in PR #1: `EvidenceIngestor` (platform-agnostic ingestion with format routing), `Pass1Runner` (NER + embedding pipeline), `ingest_evidence` / `run_pass1_analysis` / `evidence_search` MCP tools registered.
- Fixed: DuckDbVault now exposes `hashContent()` and `getIngestionByHash()` delegation methods; SmsXmlParser metadata type extended with optional MMS/call fields.
- Remaining: a dedicated DuckDB read/query tool; replacement of the TS `switch` dispatch with a registry pattern.

Sources: `docker-compose.yml`, `infrastructure/core/config.json`, `mcp-servers/ts-mcp-server/src/index.ts`, `mcp-servers/ts-mcp-server/src/tools/EvidenceIngestor.ts`, `mcp-servers/ts-mcp-server/src/tools/Pass1Runner.ts`

## Phase B: Parser Coverage

Status: in progress

- Done: SMS XML parsing, Facebook export parsing, iMessage PDF parsing.
- Added in PR #1: Multi-engine document intelligence framework scaffolded (`mcp-servers/py-mcp-server/src/document_intelligence/`) with 11 engine stubs (Pandoc, Tesseract, DocTR, Docling, OCRopus, Unstructured, Google DocAI, AWS Textract, LlamaParse, IBM watsonx, GLM-OCR). Directus flow trigger for evidence upload added.
- Remaining: Pandoc engine stub → working implementation (Phase 1 task 1.4-02); Tesseract engine stub → working implementation (Phase 1 task 1.4-03); WhatsApp TXT, ChatGPT export, Google Timeline, archive extraction.

Sources: `mcp-servers/ts-mcp-server/src/tools/SmsXmlParser.ts`, `mcp-servers/ts-mcp-server/src/tools/FacebookExportParser.ts`, `mcp-servers/ts-mcp-server/src/tools/ImessagePdfParser.ts`, `mcp-servers/py-mcp-server/src/document_intelligence/`

## Phase C: Semantic and Identification Tooling

Status: in progress

- Done: 26 Python MCP tools exposed through `server.py`, covering Semantica extraction, provenance, Neo4j queries, LanceDB operations, DPK pre-processing, voice fingerprinting, user-detection placeholders, and workflow execution. Document intelligence tools registered as plugin.
- Remaining: end-to-end validation on real evidence; embedding pipeline wired to `EvidenceIngestor`; LanceDB write path from `Pass1Runner`.

Sources: `mcp-servers/py-mcp-server/src/server.py`, `mcp-servers/py-mcp-server/src/tools/dpk_tools.py`, `mcp-servers/py-mcp-server/src/tools/workflow_tools.py`, `mcp-servers/py-mcp-server/src/tools/voice_tools.py`, `mcp-servers/py-mcp-server/src/tools/user_detection.py`

## Phase D: Security and Routing Hardening

Status: in progress

- Done: Keycloak service is present in Compose, DIAL settings include JWT verification config, role/key configuration exists in `config.json`, and Caddy fronts the stack.
- Remaining: verify the auth flow end to end, tighten the proxy toward real HTTPS deployment, and resolve any stale model or routing entries such as local-only placeholders that contradict project policy.

Sources: `docker-compose.yml`, `infrastructure/settings/settings.json`, `infrastructure/core/config.json`, `infrastructure/Caddyfile`

## Phase E: Frontend and Analyst Experience

Status: early scaffold

- Done: a Vite/React app exists with CopilotKit and Radix dependencies installed. Directus added to docker-compose (profile-gated, requires owner approval to activate).
- Remaining: Directus activation (task E-02); replace the starter UI with the actual analyst workflow, connect it to DIAL/auth, and implement review/timeline/entity-resolution surfaces.

Sources: `client/package.json`, `client/src/App.tsx`, `client/src/main.tsx`, `docker-compose.yml`

## Phase F: Federation and Advanced Platform Features

Status: planned

- WunderGraph Cosmo federation is still planned rather than implemented in the checked-in stack.
- More advanced forensic workflows such as hindsight analysis, contradiction packaging, and legal evidence assembly remain planned.

Sources: `docs/architecture/ARCHITECTURE.md`, `docs/archive/plans/IMPLEMENTATION_HANDOFF.md`

## Notes on Historical Planning

Historical requirement and plan material still exists under `docs/wiki/.plannotator/` and other recovered planning folders, but this roadmap is the live status page. The detailed sprint tasks and phase gate structure are captured in `SPRINT_PLAN.md` and `IMPLEMENTATION_PHASE_PLAN.md`.

Sources: `docs/references/PLANNOTATOR.md`, `SPRINT_PLAN.md`, `IMPLEMENTATION_PHASE_PLAN.md`

## Change Log

- 2026-04-11, rev 3, Copilot: Updated to reflect PR #1 additions (EvidenceIngestor, Pass1Runner, document intelligence framework, Directus, planning suite). Added Phase 0 status. Fixed TypeScript build errors.
- 2026-04-08, rev 2, Codex: rewrote the roadmap to reflect the checked-in codebase instead of older aspirational phase claims.
