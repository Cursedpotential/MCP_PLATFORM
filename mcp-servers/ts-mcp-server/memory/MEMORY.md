# TS MCP Server — Session Memory
> Domain-level session log for mcp-servers/ts-mcp-server/.
> Read AFTER: GROUND_TRUTH.md → AGENTS.md → memory/MEMORY.md (root) → memory/MATT.md → local AGENTS.md
> Commit after every session that touches this domain.

---

## DOMAIN SCOPE

This memory file tracks work in: `mcp-servers/ts-mcp-server/`

**This domain owns:**
- All message parsers (SMS working, Facebook/iMessage stubs)
- DuckDB vault operations (T1 — first touch, SHA-256)
- PostgreSQL writes (T4)
- Review queue (HITL approve/reject)
- Evidence ingestor router
- Pass 1 runner

**Key tools/services:**
- DuckDB (embedded, file-based)
- PostgreSQL (port 5432)
- ReviewQueue.ts
- EvidenceIngestor.ts

**Key files:**
- src/tools/SmsXmlParser.ts (WORKING)
- src/tools/FacebookExportParser.ts (STUB)
- src/tools/ImessagePdfParser.ts (STUB)
- src/tools/DuckDbVault.ts
- src/tools/PostgresWriter.ts
- src/tools/ReviewQueue.ts
- src/tools/EvidenceIngestor.ts
- src/tools/Pass1Runner.ts

---

## CURRENT STATE

> Update this section at the start of each session based on the last SESSION LOG entry.

- **Last worked on**: [date and agent]
- **Current status**: [one sentence — what state is this domain in right now]
- **Blocking issues**: [none / list]
- **Next approved task**: [task ID from TODO.md or "pending Matt's direction"]

---

## SESSION LOG

---

### SESSION: 2026-04-20
**Agent**: Perplexity Computer (external — not a coding agent)
**Model**: N/A
**Tool**: Perplexity Computer chat

**What was done**:
- Memory hierarchy scaffolded — this file created
- Context management architecture designed

**Files modified**: This file created.

**Decisions made**: Memory is filesystem-based, committed to repo after each session.

**Open threads**: All implementation work pending. No coding sessions have run in this domain yet.

**What comes next**: Pull repo locally, begin coding sessions using system prompt v2.

---

## SESSION LOG TEMPLATE

```
### SESSION: YYYY-MM-DD
**Agent**: [name/role]
**Model**: [GLM-5 / Gemini 3.1 / Claude Opus / Kimi 2.5 / Nemotron / other]
**Tool**: [OpenCode / Claude Code / Antigravity / other]

**What was done**:
- [bullet list]

**Files modified**:
- [path] — [what changed]

**Decisions made**:
- [any decisions, even small ones]

**HITL gates hit**:
- [gate type] — [approved / pending / deferred]

**Alpha 1 assets ported**:
- [Alpha 1 path] → [Alpha 2 path]

**Open threads**:
- [anything incomplete for next session]

**What comes next**:
- [specific next task]

**Matt's mood/state**:
- [brief honest note]
```
