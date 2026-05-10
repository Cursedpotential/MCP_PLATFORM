---
name: memory-write
description: Execute session-end memory write-back cascade — update MEMORY.md files deepest to root, commit, push
---
Execute mandatory session end write-back: Step 1 update TODO.md files deepest to root marking tasks complete or in-progress with next step, bubble one-liner to parent. Step 2 update MEMORY.md files deepest to root — full session detail at deepest level including files modified decisions made blockers parity notes and session trace JSON, summary paragraph at each parent, one-liner at root with link to domain memory. Step 3 git add memory and all modified domain memory and TODO files. Step 4 git commit with message memory colon session log YYYY-MM-DD dash one line summary. Step 5 run bash scripts/check-guardrails.sh staged. Step 6 git push origin main. Step 7 emit SESSION END block with Agent Date Tasks completed Tasks in-progress Blockers Decisions Memory cascade written Pushed commit hash.
