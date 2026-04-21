---
name: session-start
description: Begin a new dev session — sync repo, read context files, emit SESSION START block
---
Run git pull origin main. Then read in order: GROUND_TRUTH.md, AGENTS.md, memory/MEMORY.md, memory/MATT.md, INDEX.md, TODO.md, docs/wiki/alpha1-inventory.md, ORCHESTRATION_CONTRACT.md. After reading all files emit SESSION START block with fields: Agent, Date, Context A, Platform phase, Last session, Files read Phase 1, Current approved task, Open blockers. Then stop and ask: What are we working on today?
