# Utilities Catalog Categories

This page defines the category, source, and disposition vocabulary for the `tools/utilities` intake catalog.

## Categories

- `mcp-server`: staged MCP server candidates under `tools/utilities/mcp-servers/`
- `application`: standalone tools with a UI, backend, or deployable workflow
- `suite`: grouped multi-tool bundles such as `Context_Analysis_Suite` and `Voice_Analysis`
- `script-pack`: operational scripts or script collections, especially `tools/utilities/scripts/`
- `library`: reusable code assets, downloaded libraries, or loose source artifacts intended for adaptation
- `parser`: data-format or evidence-import focused tools
- `prompt-pack`: prompt libraries, directive sets, and ideation packs
- `vendor-source`: vendored upstream repositories kept for reference or future adaptation
- `extracted-source`: `_extracted_*` snapshots or unpacked upstream trees
- `reference-artifact`: loose docs, scans, prompts, and stale indexes that should not be treated as runtime assets

## Source Types

- `custom`: created in-house for this workspace or a closely related workspace
- `adapted`: local tool derived from or built around external source material
- `vendored`: upstream repository or downloaded library stored in-tree
- `extracted`: extracted snapshot or unpacked source retained as reference
- `reference`: documentation or artifact kept for context instead of execution
- `mixed`: container that holds multiple source types

## Disposition States

- `active`: currently used or treated as an active operational asset
- `integrate`: near-term integration candidate
- `evaluate`: worth reviewing for adaptation, wrapping, or selective reuse
- `archive`: retain only as reference or move out of the active intake path
- `redundant`: duplicate or superseded copy; do not treat as canonical

## Default Rules

- `sbv-main` defaults to `integrate`
- staged MCPs default to `evaluate` unless they are already clearly adopted
- `scripts/` defaults to `active` as a pack, while duplicate ` (2)` files default to `redundant`
- `_extracted_*` directories default to `archive`
- loose root artifacts like stale indexes and scans default to `reference-artifact` and usually `archive`

Sources: `tools/utilities`, `tools/utilities/mcp-servers`, `tools/utilities/scripts`
