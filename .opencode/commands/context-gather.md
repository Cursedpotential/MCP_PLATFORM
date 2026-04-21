---
description: Gather full context on a task area before implementation — reads domain cascade, checks Alpha 1, emits STEP-BACK ANALYSIS
agent: context-gather
---

Gather complete context before any implementation. Task area: $ARGUMENTS

## Phase 2 — Domain cascade (read inward from repo root to the task area)

For the task area provided, identify the directory hierarchy and read each level:
- [domain]/AGENTS.md
- [domain]/memory/MEMORY.md
- [domain]/INDEX.md
- [domain]/TODO.md

Repeat for each subdirectory level until you reach the exact working directory.

## Alpha 1 check

Search the Alpha 1 reference repo (https://github.com/Cursedpotential/mcp-tool-platform) for any existing implementation of this task:
- What files exist that are relevant?
- What field coverage / schema do they define?
- Decision: PORT FROM ALPHA 1 | EXTEND EXISTING | NEW

## STEP-BACK ANALYSIS

Emit the full analysis:

```
STEP-BACK ANALYSIS — [task name]

Q1 — EXISTENCE CHECK
  Alpha 2 path checked: [path or "searched — not found"]
  Alpha 2 finding: [what exists, or "not found"]
  Alpha 1 path checked: [URL]
  Alpha 1 finding: [what exists, or "not found"]
  Decision: [ PORT FROM ALPHA 1 | EXTEND EXISTING | NEW ]
  Justification if NEW: [why no existing file can be extended]

Q2 — DEPENDENCY CHECK
  What must be complete before this task can succeed?
    [ ] [dependency 1] — status: [complete / stub / missing]
    [ ] [dependency 2] — status: [complete / stub / missing]

Q3 — SCOPE BOUNDARY
  Files I will modify: [explicit list — only these files]
  Files I will NOT touch: [explicit list]
  Any file changing >30%: [flag as REWRITE — requires separate approval]

Q4 — RISK SURFACE
  What could break if I do this wrong?
    - [risk 1]
    - [risk 2]

Q5 — APPROVAL GATE CHECK
  Does this task require "approved — proceed" before I act? [ YES / NO ]
  If YES — have I received it? [ Quote exact words or STOP ]
```

Do not write any code. Present the analysis and wait for "approved — proceed".
