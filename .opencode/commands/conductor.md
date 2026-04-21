---
description: Conductor OSS operations — define workflows, start executions, check status, signal tasks, query task queues
agent: conductor
---

Conductor OSS operation: $ARGUMENTS

Before any Conductor operation:
1. Read docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md — verify the gate status
2. Check if CONDUCTOR GATE is lifted: look for `// GATE-LIFTED` in any workflow definition in the repo
3. If gate is NOT lifted, report: "CONDUCTOR GATE is not lifted. First end-to-end ingest test must pass before workflow definitions can be committed. I can help design and document the workflow but cannot commit it."

If gate IS lifted, proceed with the requested operation using the Conductor CLI or REST API per docs/wiki/skills/orchestration/conductor/OSS_REFERENCE.md.

For workflow design questions, reference:
- docs/wiki/skills/orchestration/conductor/OVERVIEW.md — concepts
- docs/wiki/skills/orchestration/conductor/OSS_REFERENCE.md — API + CLI reference
- docs/wiki/skills/orchestration/conductor/ECOSYSTEM.md — MCP server, AI cookbook

Worker task type naming convention (from mcp-servers/AGENTS.md):
- Format: PLATFORM_[DOMAIN]_[ACTION] (e.g., PLATFORM_INGEST_SMS_XML, PLATFORM_REVIEW_APPROVE)
