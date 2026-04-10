---
title: Tools and Utilities Intake Catalog
reviewed: 2026-04-08
revision: 1
author: Codex
status: current
---

# Tools and Utilities Intake Catalog

This catalog is the hard copy for the mixed intake library at `tools/utilities/`. It covers staged tools, vendored source drops, extracted references, loose artifacts, and operational scripts that are not the same thing as the live repo MCP servers.

The repo MCP server index remains at [tools index](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/INDEX.md).

## Overview

The `tools/utilities` tree is a mixed depot. It currently contains:

- full applications and suites that may be integrated or adapted
- staged external MCP servers under `tools/utilities/mcp-servers/`
- an active operational script pack under `tools/utilities/scripts/`
- vendored and extracted upstream source trees retained for evaluation
- loose handoff docs, scans, prompts, and stale indexes that should not be treated as authoritative

This catalog classifies each record by:

- `category`: what the item is
- `source_type`: where it came from
- `status`: `active`, `integrate`, `evaluate`, `archive`, or `redundant`

## Catalog Sections

- [Category rules](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/categories.md)
- [Machine-readable manifest](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/manifest.json)
- [Applications and suites](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/apps/INDEX.md)
- [Staged MCP servers](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/mcp-servers/INDEX.md)
- [Operational scripts](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/scripts/INDEX.md)
- [Vendored and extracted sources](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/vendor/INDEX.md)
- [Loose artifacts and stale indexes](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/artifacts/INDEX.md)

## Current Guidance

### Integrate

- [SBV](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/apps/sbv-main.md) is the clearest near-term integration target in this intake library.

### Evaluate

- The staged external MCP set under [utilities/mcp-servers](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utilities/mcp-servers/INDEX.md) should be reviewed one-by-one for wrapping, adaptation, or direct adoption.
- Utility applications like `Chunker`, `ConversationExtractor`, `context-relay`, `context-artifact-resolver`, `lexicon-analysis-engine`, and `stirling_pdf_tool` are cataloged as evaluation candidates, not yet as live components.
- Vendored trees such as `graphql-eslint`, `magentic-main`, and `mashumaro-master` are retained as source assets, not active runtime dependencies.

### Archive or mark redundant

- `_extracted_*` trees default to archived reference material.
- Root `INDEX.md`, `index.json`, `baseline_scan.json`, and duplicate docs like `README (2).md` are stale artifacts.
- Script duplicates with ` (2)` suffix are marked `redundant` in the manifest and should not be treated as canonical.

## Structure Notes

- This pass only flattens the tools area of the wiki.
- The older `docs/wiki/tools/utility/` subtree is kept for the existing per-script pages, but the authoritative intake index now lives here.
- A broader documentation flattening pass is still needed outside the tools area.

## TODO

- Flatten the wider documentation IA after the tools catalog has stabilized.
- Decide which evaluation candidates should move from intake storage into the live product architecture.
- Archive or relocate clearly stale artifacts after downstream references are updated.

Sources: `tools/utilities`, `tools/utilities/mcp-servers`, `tools/utilities/scripts`, `docs/wiki/tools/utility/INDEX.md`
