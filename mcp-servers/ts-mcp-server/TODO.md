# TS MCP Server TODO
> Read parent first: mcp-servers/TODO.md
> Only Matt can move tasks from READY → APPROVED.
> Agents update IN_PROGRESS and DONE as they work. Commit after every change.

---

## Status Key: IDEA → READY → APPROVED → IN_PROGRESS → DONE → DEFERRED → BLOCKED

## Active Tasks

| ID | Task | Status | Approved | Depends On | Assigned Session |
|----|------|--------|----------|------------|-----------------|
| TS-001 | Verify SMS parser against Alpha 1 production schema — audit only | READY | NO | — | — |
| TS-002 | Port production-message-schemas.ts from Alpha 1 — present merge plan first | READY | NO | TS-001 | — |
| TS-003 | Facebook parser: stub → working (port from Alpha 1 loaders/) | READY | NO | TS-002 | — |
| TS-004 | iMessage parser: stub → working (port from Alpha 1 loaders/) | READY | NO | TS-002 | — |
| TS-005 | MessageNormalizer shared utility (dedup normalization logic) | READY | NO | TS-003 TS-004 | — |
| TS-006 | DuckDB dedup SHA-256 fingerprint check wired to all parsers | READY | NO | TS-003 TS-004 | — |
| TS-007 | Chain of custody module port from Alpha 1 custody/ | READY | NO | — | — |
| TS-008 | Evidence hasher port from Alpha 1 hasher/ | READY | NO | — | — |
| TS-009 | Evidence registry port from Alpha 1 registry/ | READY | NO | — | — |
| TS-010 | Pass 1 runner — verify completeness against spec | READY | NO | TS-002 | — |
| TS-011 | Parser integration tests — round-trip fixture data | READY | NO | TS-003 TS-004 | — |

---

## Completed Tasks

| ID | Task | Completed | Session |
|----|------|-----------|---------|
| — | (none yet) | — | — |
