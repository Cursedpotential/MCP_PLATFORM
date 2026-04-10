---
title: Documentation Index
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# AI DIAL Stack Documentation

> This documentation set was re-audited by Codex on 2026-04-08 to separate live docs from archived and historical material.

## Overview

`docs/` is the canonical home for active project documentation. The live set is organized by purpose, and `docs/archive/` mirrors the same shape for superseded material.

Sources: `docs/architecture/ARCHITECTURE.md`, `docs/plans/ROADMAP.md`, `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md`

## Live Structure

- [Architecture](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/ARCHITECTURE.md) for the current system shape, live components, and planned gaps.
- [Development Guide](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/guides/DEVELOPMENT.md) for setup, workflow, and verification commands.
- [Roadmap](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/plans/ROADMAP.md) for phase status and near-term gaps.
- [Stories](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/STORIES.md) for reverse-engineered product and developer stories.
- [FAQ](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/architecture/FAQ.md) for quick answers and cross-links.
- [Spec-Driven Development](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/specs/SPEC_DRIVEN_DEVELOPMENT.md) for process and documentation rules.
- [Documentation Structure Spec](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md) for the documentation reorganization and archive rules.
- [Wiki Home](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/INDEX.md) for the wiki-style entrypoints and MCP server pages.

Sources: `docs/guides/DEVELOPMENT.md`, `docs/plans/ROADMAP.md`, `docs/wiki/INDEX.md`, `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Historical Context

- [References](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/references) holds dated migration notes and session-derived material that may still explain why a change happened.
- [Audit Notes](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/.audit) contains dated repo audits and inventories.
- [Planning Workspace](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/references/PLANNOTATOR.md) explains the `docs/wiki/.plannotator/` workspace and its compatibility symlink at `.plannotator`.
- The repo-level sidecar workspaces `.annotative`, `.full-review`, `.planning`, and `.redline` now resolve into matching directories under `docs/wiki/`.

Treat these as reference material unless a live document explicitly promotes them to current truth.

Sources: `docs/references/restructure-2026-03-16.md`, `docs/references/PLANNOTATOR.md`, `docs/.audit/2026-03-30-repo-audit.md`

## Archive

Newly archived material belongs under `docs/archive/<same-relative-path-as-live-doc>`. The archive is intentionally mirrored so old material stays discoverable without polluting the live tree.

Sources: `docs/archive/README.md`, `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Change Log

- 2026-04-08, rev 1, Codex: created a canonical documentation index and separated live, historical, and archived material.
