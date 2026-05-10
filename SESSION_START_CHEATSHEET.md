# MCP_PLATFORM — Session Start Cheat Sheet

> Copy-paste prompts for starting any coding agent session (Anti-Gravity, OpenCode, Claude Code, etc.)
> Approval language: `approved — proceed` only. Everything else = not approval.

---

## 1. BASELINE START
_Use this every session, no exceptions._

```
git pull origin main, then follow the AGENTS.md read order before doing anything.

Confirm you have read:
- MCP_PLATFORM_SYSTEM_PROMPT_V3.md
- GROUND_TRUTH.md
- ORCHESTRATION_CONTRACT.md
- [workdir]/AGENTS.md

Do not write any code until you confirm.
```

---

## 2. CONTEXT GATHER
_Add this before giving a task. Paste after the baseline start._

```
Before I give you a task, build context from the repo. Answer from files — do not theorize.

1. What is this application trying to do?
   → GROUND_TRUTH.md + README.md

2. Who uses it and what do they need from it?
   → docs/wiki, any user-facing docs

3. What is the current state of the area I'll be working in?
   → [workdir]/AGENTS.md + [workdir]/TODO.md + [workdir]/INDEX.md

4. What already exists that is relevant to this task?
   → Search the codebase before assuming nothing is there
   → For parsers/NLP tools: search MCP_Tool_Platform/server/mcp/ first (Alpha 1)

5. What are the open questions or blockers in this domain?
   → GROUND_TRUTH.md OQ section + [workdir]/TODO.md

Report back. Do not write any code yet.
```

---

## 3. TASK BRIEF
_Give this only after context gather is confirmed._

```
Task: [one specific thing]

Scope:
- [what to touch]
- [what NOT to touch]

Done when:
- [specific verifiable outcome]

Gates:
- No stubs. Production-ready only.
- No container starts without: approved — proceed [service: name]
- No changes to Semantica interfaces — flag and ask if something seems broken
- CONDUCTOR GATE is active — no Conductor workflow merges until first ingest test passes
```

---

## 4. OPTIONAL ADD-ONS

### → Conductor / Orchestration work
```
Also load before starting:
  docs/wiki/skills/orchestration/conductor/SKILL.md
  docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md
```

### → Parser / MCP server work
```
Also load before starting:
  mcp-servers/AGENTS.md
  mcp-servers/[ts|py|js]-mcp-server/AGENTS.md
Search Alpha 1 at MCP_Tool_Platform/server/mcp/ before writing anything new.
```

### → Infrastructure work
```
Also load before starting:
  infrastructure/AGENTS.md
  docs/wiki/skills/orchestration/conductor/OVERVIEW.md  ← CONDUCTOR GATE status
CONDUCTOR GATE is hard-locked. Do not start any Conductor infra work without: approved — proceed
```

### → Documentation / Wiki work
```
Also load before starting:
  docs/AGENTS.md
Rules:
- Never delete. Superseded docs move to _DEPRECATED/<mirrored-path>.
- If a doc contradicts GROUND_TRUTH.md: GROUND_TRUTH.md wins. Flag, do not silently update.
- No new architecture docs without direction.
```

### → Tightest possible context gather (quick version)
```
Before you touch anything: read the relevant files in [workdir] and tell me
what already exists that relates to [task area].
Look for: existing implementations, schemas, tool registrations.
Do not propose solutions yet.
```

---

## 5. FULL SESSION OPENER (combined, copy-paste ready)

```
git pull origin main, then follow the AGENTS.md read order before doing anything.

Confirm you have read:
- MCP_PLATFORM_SYSTEM_PROMPT_V3.md
- GROUND_TRUTH.md
- ORCHESTRATION_CONTRACT.md
- [workdir]/AGENTS.md

Then build context from the repo before I give you a task. Answer from files only — no theories.

1. What is this application trying to do?
2. Who uses it and what do they need from it?
3. What is the current state of [workdir]?
4. What already exists that is relevant to [task area]?
   (Search MCP_Tool_Platform/server/mcp/ if touching parsers or NLP tools)
5. What are the open questions or blockers here?

Report back. Do not write any code yet.
```

---

## 6. QUICK SANITY CHECK (run anytime to verify the session is wired right)

```bash
git pull && cat AGENTS.md
```

If the Conditional loads block is present and references `docs/wiki/skills/orchestration/conductor/SKILL.md` — the session is wired correctly.

---

## GROUND RULES (always in effect)

| Rule | Detail |
|------|--------|
| Approval language | `approved — proceed` only |
| No stubs | Every file must be production-ready |
| No silent rewrites | Ask before changing anything not in the task scope |
| No deletes | Move to `_DEPRECATED/` with mirrored path |
| Semantica is authoritative | Call it via CALL_MCP_TOOL — never rewrite it |
| CONDUCTOR GATE | No Conductor merges until first end-to-end ingest test passes |
| Container gate | `approved — proceed [service: name]` before any container starts |
| One task at a time | Do not accept a list — one task, done, confirmed, then next |

---

_Last updated: 2026-04-21 — MCP_PLATFORM commit e90c10d_
