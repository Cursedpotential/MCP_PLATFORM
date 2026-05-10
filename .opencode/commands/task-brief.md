---
description: Emit a concise task brief — what you're doing, what you're NOT touching, and the exit criteria
agent: platform
---

Before starting implementation of: $ARGUMENTS

Emit a task brief in this exact format:

```
TASK BRIEF — [task name]

Objective:
  [One sentence — what will be true when this task is complete]

Scope (files I will modify):
  - [file 1] — [what changes]
  - [file 2] — [what changes]

Out of scope (files I will NOT touch):
  - [file] — [why excluded]

Exit criteria:
  [ ] [measurable outcome 1]
  [ ] [measurable outcome 2]
  [ ] No stubs remaining in modified files
  [ ] Memory cascade written (MEMORY.md updated deepest → root)
  [ ] Conventional commit staged

Blockers:
  [Any unresolved OQs or gate conditions that affect this task, or NONE]

Approval required before starting? [ YES — waiting | NO — proceeding ]
```

If approval is required, STOP after emitting the brief and wait for "approved — proceed".
