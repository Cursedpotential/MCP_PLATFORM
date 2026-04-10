---
title: Documentation Structure Spec
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Documentation Structure Spec

## Objective

Establish a single live documentation structure for `dial-stack`, separate historical material from active guidance, and give future agents a predictable place to update architecture, roadmap, wiki, and prompt content.

Sources: `docs/INDEX.md`, `docs/wiki/INDEX.md`, `AGENTS.md`, `CLAUDE.md`

## Canonical Layout

- `docs/INDEX.md`: top-level map of the live docs set.
- `docs/architecture/`: current architecture, stories, and FAQ.
- `docs/guides/`: developer-facing operational guides.
- `docs/plans/`: roadmap and live planning documents.
- `docs/specs/`: process specs and change-specific documentation plans.
- `docs/wiki/`: wiki entrypoints, MCP server reference pages, and the relocated `plannotator/` workspace.
- `docs/references/`: dated or historical reference material that still has value.
- `docs/.audit/`: dated audits and inventories.
- `docs/archive/`: mirrored archive of superseded content.

Sources: `docs/INDEX.md`, `docs/references/PLANNOTATOR.md`

## Archive Strategy

Archive by mirrored path. If a live document becomes stale, move it to `docs/archive/<same-relative-path>`.

Current examples archived during this pass:

- `docs/wiki/FUCKED.MD`
- `docs/architecture/FORENSIC_EVIDENCE_PLATFORM_ARCHITECTURE_LEGACY.md`
- `docs/plans/IMPLEMENTATION_HANDOFF.md`
- `docs/specs/MCP_TOOL_CATALOG_LEGACY.md`

Sources: `docs/archive/wiki/FUCKED.MD`, `docs/archive/architecture/FORENSIC_EVIDENCE_PLATFORM_ARCHITECTURE_LEGACY.md`, `docs/archive/plans/IMPLEMENTATION_HANDOFF.md`, `docs/archive/specs/MCP_TOOL_CATALOG_LEGACY.md`

## Documentation Rules

1. Update live docs in `docs/` first. Do not treat `.planning` or `docs/wiki/plannotator/` as the system of record unless the task is explicitly about historical plans.
2. Distinguish clearly between implemented behavior, planned work, and recovered historical material.
3. New or fully rewritten canonical docs should include consistent metadata at the top: title, reviewed date, revision, author, and status.
4. Add or update a short change log section when a canonical document is materially rewritten.
5. When code changes alter behavior, update `docs/INDEX.md`, the relevant architecture or wiki page, and `docs/plans/ROADMAP.md` if phase status changes.

Sources: `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md`, `docs/plans/ROADMAP.md`, `docs/wiki/INDEX.md`

## Acceptance Criteria

- A newcomer can find the live architecture, roadmap, development guide, and MCP server docs from `docs/INDEX.md`.
- Archived files live under mirrored paths in `docs/archive/`.
- The plannotator workspace is reachable from the documentation tree while preserving compatibility at `.plannotator`.
- The reusable analysis prompt is stored as a repo skill so Codex can trigger it intentionally.

Sources: `docs/INDEX.md`, `docs/references/PLANNOTATOR.md`, `.agents/skills/dial-codebase-analysis/SKILL.md`

## Change Log

- 2026-04-08, rev 1, Codex: created the documentation structure spec and aligned it with the archive mirror and plannotator relocation.
