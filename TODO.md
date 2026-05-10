# MCP Platform — Root TODO
> Platform-level tasks and phase gates.
> Read subdirectory TODO.md files for domain-specific tasks.
> Only Matt can move tasks from READY → APPROVED.
> Agents update IN_PROGRESS and DONE status as they work.
> Commit after every status change.

---

## Status Key

| Status | Meaning |
|--------|---------|
| IDEA | Proposed, not yet scoped |
| READY | Scoped and ready for Matt's approval |
| APPROVED | Matt said "approved — proceed" |
| IN_PROGRESS | Agent actively working on it |
| DONE | Complete, verified, committed |
| DEFERRED | Deliberately postponed |
| BLOCKED | Cannot proceed — dependency or open question |

---

## Phase Gates

| Gate | Description | Status | Approved |
|------|-------------|--------|----------|
| PHASE-0 | Foundation audit — verify all tiers healthy, catalog Alpha 1 assets | READY | NO |
| PHASE-A | Core ingestion pipeline working end-to-end | IN_PROGRESS (~70%) | PARTIAL |
| PHASE-B | Embedding pipeline + semantic search working | READY | NO |
| PHASE-C | Pass 1 analysis pipeline working | READY | NO |
| PHASE-D | All core MCP tools registered and testable | READY | NO |
| PHASE-E | Directus activated, document intelligence local engines working | READY | NO |

---

## Platform-Level Active Tasks

| ID | Task | Status | Approved | Depends On | Notes |
|----|------|--------|----------|------------|-------|
| PLAT-001 | Alpha 1 full asset inventory | READY | NO | — | See HANDOFF_ALPHA1_INVENTORY.md — for documentation agent |
| PLAT-002 | Context management architecture + TODO/INDEX hierarchy | IN_PROGRESS | YES | — | Being built now |
| PLAT-003 | Wiki knowledge base build-out | READY | NO | PLAT-001 | See HANDOFF_WIKI_AND_DOCS.md |
| PLAT-004 | Document health audit + archive sort | READY | NO | — | See HANDOFF_CONTEXT_AND_ARCHIVE.md |
| PLAT-005 | ADR register updated through ADR-033 | DONE | YES | — | ADR-033: Conductor replaces Agno + n8n |
| PLAT-006 | Docker Compose — verify all service definitions correct | READY | NO | — | Pre-start verification |
| PLAT-007 | Health check endpoints on all 3 MCP servers | READY | NO | — | Phase A task |
| PLAT-008 | Production-message-schemas.ts port + merge plan | READY | NO | PLAT-001 | Present as spec first |
| PLAT-009 | Directus container activation | READY | NO | PLAT-006 | Requires CONTAINER GATE approval |
| PLAT-010 | OpenWebUI / LibreChat container definitions | READY | NO | PLAT-009 | Requires individual approval per service |

---

## Open Architectural Questions (Blocking Specific Tasks)

| ID | Question | Blocks |
|----|----------|--------|
| OQ-1 | OpenCode: server mode vs agent mode | Any OpenCode integration |
| OQ-2 | Internal API design: REST vs GraphQL vs gRPC | Conductor workers/Directus integration |
| ~~OQ-3~~ | ~~Agno deployment timing~~ | ⛔ CLOSED — ADR-033: Agno removed, Conductor replaces it |
| ~~OQ-4~~ | ~~n8n workflow trigger design~~ | ⛔ CLOSED — ADR-033: n8n removed, Conductor replaces it |
| OQ-C1 | Conductor worker deployment: containerized vs local process | Conductor deployment |
| OQ-C2 | Conductor UI access: internal only vs Keycloak-gated | Conductor deployment |
| OQ-C3 | Conductor backend: Elasticsearch vs Postgres | Conductor deployment |
| OQ-C4 | /api/chat endpoint design: routing modes | client/ work |
| OQ-C5 | Conductor HUMAN task ↔ ReviewQueue bridge design | HITL gate implementation |
| OQ-5 | Embedding model selection | PHASE-B work |

---

## Completed Tasks

| ID | Task | Completed | Session |
|----|------|-----------|---------|
| — | Project initialized, CLAUDE.md + AGENTS.md created | 2026-03-17 | Unknown |
| — | Memory system rebuilt, system prompt v2, GROUND_TRUTH.md | 2026-04-20 | Perplexity Computer |
