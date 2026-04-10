---
title: Archive Policy
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Documentation Archive

## Overview

`docs/archive/` mirrors the live `docs/` structure. Archive stale or superseded files into the matching relative path so the lookup path stays predictable.

Examples:

- `docs/architecture/ARCHITECTURE.md` archives to `docs/archive/architecture/ARCHITECTURE.md`
- `docs/plans/ROADMAP.md` archives to `docs/archive/plans/ROADMAP.md`
- `docs/wiki/tools/py-mcp-server.md` archives to `docs/archive/wiki/tools/py-mcp-server.md`

Sources: `docs/INDEX.md`, `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Rules

1. Archive by mirrored path, never by dumping unrelated files into one flat folder.
2. Keep active documents in `docs/`; archived copies live only in `docs/archive/`.
3. When replacing a live document, update the live index pages so they point to the new canonical file.
4. Rough notes, session transcripts, and one-off handoffs should be archived if they are no longer live operating guidance.

Sources: `docs/specs/DOCUMENTATION_STRUCTURE_2026-04-08.md`

## Change Log

- 2026-04-08, rev 1, Codex: established mirrored archive rules for the reorganized docs tree.
