---
description: Execute the session-end memory write-back cascade — update MEMORY.md files deepest to root, commit, push
agent: platform
---

Execute the mandatory session-end write-back protocol. Task area: $ARGUMENTS

## STEP 1 — Update TODO.md files (deepest → root)
For each directory level you worked in:
- Mark completed tasks as `[x]`
- Mark in-progress tasks with current next step
- Bubble a one-line status up to parent TODO.md
- Update root TODO.md only if a root-level task changed

## STEP 2 — Update MEMORY.md files (deepest → root)
- Append FULL SESSION DETAIL to deepest workdir memory/MEMORY.md:
  - Date, agent, task completed
  - Files modified (list every file)
  - Decisions made (schema changes, architecture choices)
  - Blockers raised
  - Parity notes (Alpha 1 vs Alpha 2)
  - Session trace JSON (copy template from memory file header)
- Append SUMMARY PARAGRAPH to each parent memory/MEMORY.md
- Append ONE-LINER to root memory/MEMORY.md with link to domain memory

## STEP 3 — Stage memory files
```
git add memory/
git add [all modified domain]/memory/
git add [all modified domain]/TODO.md
```

## STEP 4 — Commit
```
git commit -m "memory: session log YYYY-MM-DD — [one line summary]"
```

## STEP 5 — Run guardrail check
```
bash scripts/check-guardrails.sh --staged
```
If it fails, fix before pushing.

## STEP 6 — Push
```
git push origin main
```

## STEP 7 — Emit SESSION END block
```
SESSION END
Agent:             [model/tool name]
Date:              [YYYY-MM-DD HH:MM]
Tasks completed:   [list]
Tasks in-progress: [list — include next step for each]
Blockers raised:   [list — each needs Matt's attention]
Decisions made:    [platform-level decisions, or NONE]

Memory cascade written (deepest → root):
  [deepest domain]/memory/MEMORY.md    ✓ full detail
  [parent domain]/memory/MEMORY.md     ✓ summary paragraph
  memory/MEMORY.md                     ✓ one-liner

Pushed: [commit hash]
```
