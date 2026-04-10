---
title: Spec-Driven Development Process
reviewed: 2026-04-08
revision: 2
author: Codex
status: current
---

# Spec-Driven Development Process

## Core Principle

No material code or architecture change should land without a written plan in `docs/specs/` or another clearly linked live document inside `docs/`.

Sources: `AGENTS.md`, `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Canonical Documentation Locations

| Location | Purpose |
|----------|---------|
| `docs/INDEX.md` | Canonical map of the live documentation tree |
| `docs/architecture/ARCHITECTURE.md` | Current system architecture and implementation status |
| `docs/plans/ROADMAP.md` | Live phase status and delivery gaps |
| `docs/guides/DEVELOPMENT.md` | Contributor workflow and setup |
| `docs/specs/` | Change-specific specs and process documents |
| `docs/wiki/` | Wiki-style reference pages and MCP server documentation |
| `docs/archive/` | Mirrored archive for superseded material |

Treat `.planning/` and `docs/wiki/plannotator/` as historical or parallel planning context unless the work is explicitly about those workspaces.

Sources: `docs/INDEX.md`, `docs/references/PLANNOTATOR.md`

## Process

### 1. Plan

1. Read the current live docs in `docs/`.
2. Identify the exact behavior, service, or documentation area being changed.
3. Write or update a spec in `docs/specs/` when the change is non-trivial.

### 2. Implement

1. Follow coordinator and chain-of-custody constraints.
2. Keep implemented behavior and planned behavior clearly separated in code comments and docs.
3. Preserve the read-only boundary around `MCP_Tool_Platform/`.

### 3. Verify

1. Run the most relevant local build or test commands that exist.
2. Update the matching live docs.
3. Archive superseded docs under the mirrored path in `docs/archive/`.

Sources: `AGENTS.md`, `docs/archive/README.md`, `docs/guides/DEVELOPMENT.md`

## Documentation Rules

1. Prefer current truth in `docs/` over stale instructions in recovered planning files.
2. Update `docs/plans/ROADMAP.md` when phase status changes.
3. Update `docs/wiki/` when MCP tools or service capabilities change.
4. When fully rewriting a canonical doc, include metadata at the top and a short change log section.
5. If a live document becomes stale, move it into the mirrored location in `docs/archive/`.

Sources: `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`, `docs/wiki/INDEX.md`

## Anti-Patterns

| Pattern | Why It Is Wrong |
|---------|-----------------|
| Describing planned features as already shipped | Creates stale architecture docs and bad implementation assumptions |
| Updating only historical planning files | Leaves live docs wrong |
| Direct evidence writes that bypass chain-of-custody tooling | Violates forensic rules |
| Treating `.plannotator` as the live docs system of record | Mixes historical planning with active guidance |

Sources: `AGENTS.md`, `docs/references/PLANNOTATOR.md`

## Change Log

- 2026-04-08, rev 2, Codex: rewrote the process doc to point at the actual live docs tree and archive workflow.
