---
name: dial-codebase-analysis
description: Analyze the AI DIAL Stack codebase and update its documentation set. Use when the task is to audit the repo, refresh stale docs, map modules and features, or produce architecture/wiki/stories/development updates for dial-stack.
---

# DIAL Codebase Analysis

Use this skill when asked to analyze `dial-stack`, refresh architecture docs, build or update the wiki, or reconcile code and documentation.

## Scope

Focus on the live documentation tree under `docs/`. Treat `docs/wiki/.plannotator/`, `docs/references/`, `docs/.audit/`, and `docs/archive/` as historical context unless the task specifically targets them.

## Required Outputs

Update these files when they are relevant to the analysis:

- `docs/INDEX.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/guides/DEVELOPMENT.md`
- `docs/architecture/STORIES.md`
- `docs/architecture/FAQ.md`
- `docs/plans/ROADMAP.md`
- `docs/wiki/INDEX.md`
- `docs/wiki/tools/INDEX.md`
- any affected MCP server page under `docs/wiki/tools/`

If a live document is superseded, move it to the mirrored path under `docs/archive/`.

## Workflow

1. Audit the real codebase first.
   Read `docker-compose.yml`, `infrastructure/`, `mcp-servers/`, `client/`, and the current live docs.
2. Separate live behavior from planned behavior.
   Do not describe planned components as implemented.
3. Check planning history only after the live code audit.
   Use `docs/wiki/.plannotator/`, `.planning/`, `docs/references/`, and `docs/.audit/` to explain history or gaps, not to override live code.
4. Update docs in small passes.
   Refresh one area at a time, then continue.
5. Keep archive paths mirrored.
   Example: `docs/wiki/tools/py-mcp-server.md` archives to `docs/archive/wiki/tools/py-mcp-server.md`.

## Documentation Shape

### `docs/INDEX.md`

- top-level map of live docs
- live vs historical vs archive guidance

### `docs/architecture/ARCHITECTURE.md`

- overview
- high-level architecture
- major modules
- data surfaces
- implemented vs planned
- also see

### `docs/guides/DEVELOPMENT.md`

- tech stack
- environment setup
- repository structure
- workflow
- verification

### `docs/architecture/STORIES.md`

- epics
- user and developer stories
- main entry points

### `docs/architecture/FAQ.md`

- concise Q/A cross-linking back to the live docs

### `docs/wiki/`

- concise reference pages only
- no broken links to nonexistent skill or tool trees

## Source Rules

- Ground every substantive claim in checked-in files.
- Prefer file paths and concrete entry points.
- When uncertain, state that the behavior is planned, partial, or implied rather than asserting it as live.

## Conventions

- New or fully rewritten canonical docs should include top metadata: title, reviewed date, revision, author, status.
- Add a short `Change Log` section when materially rewriting a canonical doc.
- Preserve the read-only boundary around `MCP_Tool_Platform/`.
