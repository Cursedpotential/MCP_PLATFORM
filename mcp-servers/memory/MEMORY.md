# MCP Servers Layer — Session Memory
> Domain-level session log for mcp-servers/.
> Read AFTER: GROUND_TRUTH.md → AGENTS.md → memory/MEMORY.md (root) → memory/MATT.md → local AGENTS.md
> Commit after every session that touches this domain.

---

### SESSION TRACE JSON TEMPLATE
```json
{
  "trace_id": "YYYY-MM-DD-[domain]-[n]",
  "task": "[task name]",
  "files_modified": [],
  "alpha1_consulted": true,
  "gate_triggered": "[gate name or null]",
  "human_approval_received": true,
  "outcome": "COMPLETE|PARTIAL|BLOCKED",
  "notes": "[one line]"
}
```

---

## READ PROTOCOL (mandatory — every session start)

**Phase 1 (root reads — always first):**
```
git pull origin main
Read: GROUND_TRUTH.md → AGENTS.md → memory/MEMORY.md (root) → memory/MATT.md → INDEX.md → TODO.md → docs/wiki/alpha1-inventory.md → ORCHESTRATION_CONTRACT.md
```

**Phase 2 (domain cascade — read from root inward to your working directory):**
Read each level in order:
- `[domain]/AGENTS.md` → `[domain]/memory/MEMORY.md` → `[domain]/INDEX.md` → `[domain]/TODO.md`
- Then the next subdirectory level, and so on down to your target directory.

**After Phase 1 + Phase 2: emit SESSION START block and STOP. Do not write code before emitting it.**

## WRITE-BACK PROTOCOL (mandatory — every session end)

```
STEP 1: Update TODO.md deepest → root (mark tasks, bubble one-liner up)
STEP 2: Append to THIS MEMORY.md — full detail here, summary paragraph at parent, one-liner at root
STEP 3: git add memory/ + all modified domain memory/ + domain TODO.md
STEP 4: git commit -m "memory: session log YYYY-MM-DD — [one line]"
STEP 5: bash scripts/check-guardrails.sh --staged
STEP 6: git push origin main
```


## DOMAIN SCOPE

This memory file tracks work in: `mcp-servers/`

**This domain owns:**
- Cross-server coordination rules
- Shared tool registration patterns
- Port assignments and health checks

**Key tools/services:**
- TS MCP Server (8081)
- Py MCP Server (8082)
- JS MCP Server (8083)

**Key files:**
- mcp-servers/AGENTS.md
- mcp-servers/ts-mcp-server/src/
- mcp-servers/py-mcp-server/src/
- mcp-servers/js-mcp-server/src/

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


### SESSION: 2026-04-21
**Agent**: Perplexity Computer (orchestration — not a coding agent)
**Model**: N/A
**Tool**: Perplexity Computer chat

**What was done**:
- AGENTS.md updated — worker task type naming convention added (PLATFORM_[DOMAIN]_[ACTION])
- mcp-servers/AGENTS.md — Conductor skill conditional load block added

**Files modified**:
- mcp-servers/AGENTS.md — Conductor skill section added

**Decisions made**:
- Worker task type naming: PLATFORM_[DOMAIN]_[ACTION] (e.g., PLATFORM_INGEST_SMS_XML)
- Conductor replaces n8n for workflow orchestration — CONDUCTOR GATE still active

**HITL gates hit**:
- CONDUCTOR GATE — not lifted (pending first end-to-end ingest test)

**Open threads**:
- Port priority #1: facebook parser (verify Alpha 1 source first)
- Port priority #2: iMessage parser (verify Alpha 1 source first)

**What comes next**:
- Port priority #1: facebook parser (verify Alpha 1 source first)
- Port priority #2: iMessage parser (verify Alpha 1 source first)

**Session trace**:
```json
{
  "trace_id": "2026-04-21-mcp-servers-1",
  "task": "session continuity — architecture update + tooling",
  "files_modified": ['mcp-servers/AGENTS.md'],
  "alpha1_consulted": false,
  "gate_triggered": "CONDUCTOR_GATE",
  "human_approval_received": false,
  "outcome": "COMPLETE",
  "notes": "ADR-033 architecture snapshot updated; Agno/n8n references removed from active files"
}
```

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
