---
name: conductor-op
description: Conductor OSS operations — check gate status, design or run workflows, query task queues
---
Before any Conductor operation read docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md and check if CONDUCTOR GATE is lifted by looking for GATE-LIFTED marker in any workflow definition in the repo. If gate is not lifted report that the CONDUCTOR GATE requires first end-to-end ingest test to pass before workflow definitions can be committed, offer to design and document only. If gate is lifted proceed with the requested operation per docs/wiki/skills/orchestration/conductor/OSS_REFERENCE.md. Worker task type naming convention is PLATFORM underscore DOMAIN underscore ACTION for example PLATFORM_INGEST_SMS_XML.
