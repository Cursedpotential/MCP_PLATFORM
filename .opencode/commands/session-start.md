---
description: Begin a new dev session — sync repo, read all context files, emit SESSION START block, stop and wait for task
agent: platform
---

Execute the mandatory session start protocol. Follow these steps exactly — do not skip any step, do not combine steps, do not start work.

## STEP 0 — Sync
```
git pull origin main
```
Report the result (up to date / N commits pulled / conflict).

## Phase 1 — Root reads (in order)
Read each file. Do not summarize. Hold the content.
1. GROUND_TRUTH.md
2. AGENTS.md
3. memory/MEMORY.md
4. memory/MATT.md
5. INDEX.md
6. TODO.md
7. docs/wiki/alpha1-inventory.md
8. ORCHESTRATION_CONTRACT.md

## SESSION START block
After reading Phase 1, emit this exact block and STOP:

```
SESSION START
Agent:            [your model/tool name]
Date:             [YYYY-MM-DD HH:MM]
Context A:        [what tool you are — e.g., Claude Code, OpenCode, Anti-Gravity]
Platform phase:   [from GROUND_TRUTH.md]
Last session:     [date + one-line summary from memory/MEMORY.md]

Files read (Phase 1):
  GROUND_TRUTH.md               ✓
  AGENTS.md                     ✓
  memory/MEMORY.md              ✓
  memory/MATT.md                ✓
  INDEX.md                      ✓
  TODO.md                       ✓
  docs/wiki/alpha1-inventory.md ✓
  ORCHESTRATION_CONTRACT.md     ✓

Files read (Phase 2 — domain cascade):
  [not yet read — waiting for task]

Current approved task:  [from root TODO.md, or NONE]
Open blockers:          [list from MEMORY.md, or NONE]

What are we working on today?
```

Do not write code. Do not propose anything. Emit the block and wait.
$ARGUMENTS
