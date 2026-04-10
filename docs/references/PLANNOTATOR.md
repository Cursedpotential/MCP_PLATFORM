---
title: Plannotator Reference
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Plannotator Workspace

## Overview

The repository now keeps the real plannotator workspace under `docs/wiki/.plannotator/`. The root `.plannotator` path is a compatibility symlink pointing at that location.

Use this workspace for historical plans, draft governance material, review artifacts, and recovered planning traces. Do not treat it as the canonical live docs set unless a task explicitly targets that workspace.

Sources: `.plannotator`, `docs/wiki/.plannotator/`

## Key Areas

- `docs/wiki/.plannotator/plans/`: approved, denied, and annotated plan files.
- `docs/wiki/.plannotator/history/`: historical plan run outputs and recovered plan histories.
- `docs/wiki/.plannotator/drafts/`: draft governance and planning material.
- `docs/wiki/.plannotator/.planning/`: duplicated or recovered planning reference files.
- `docs/wiki/.plannotator/.full-review/`: consolidated review artifacts.
- `docs/wiki/.plannotator/.annotative/`: annotations metadata.

Sources: `docs/wiki/.plannotator/plans`, `docs/wiki/.plannotator/history`, `docs/wiki/.plannotator/drafts`, `docs/wiki/.plannotator/.planning`, `docs/wiki/.plannotator/.full-review`, `docs/wiki/.plannotator/.annotative/README.md`

## Usage Guidance

1. Promote durable guidance from plannotator into `docs/` before treating it as current operating doctrine.
2. Keep live architecture and roadmap updates in `docs/`, not in plannotator.
3. Preserve the `.plannotator` symlink so existing tools or habits still resolve correctly.
4. Treat the sibling wiki-side workspaces `.annotative`, `.full-review`, `.planning`, `.redline`, and `temp_docs` as supporting context, not primary live docs.

Sources: `docs/INDEX.md`, `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md`

## Change Log

- 2026-04-08, rev 1, Codex: documented the relocated plannotator workspace and compatibility symlink.
