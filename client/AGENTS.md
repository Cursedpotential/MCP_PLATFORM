# AGENTS.md — client/

> Domain rules for the React client. Read after root AGENTS.md.

## This domain owns
React shell, NLUX `@nlux/react` chat component (`<AiChat />`), CopilotKit HITL review integration, `/api/chat` endpoint contract.

## Current state
Scaffolded React/Vite app. CopilotKit installed but stub only. NLUX not yet wired.

## Domain-specific rules
- Do not document the client as finished until the code actually supports it.
- NLUX `<AiChat />` connects to a single `/api/chat` endpoint. Do not build multiple chat backends.
- `/api/chat` routes three modes: `plain` (LiteLLM), `tools` (ContextForge MCP), `workflow` (Conductor). Design is an open question — do not implement until Matt decides.
- CopilotKit HITL gates must sync with `app.review_queue` in the database. No orphaned UI approvals.
- No new npm dependencies without REQUIRES_CONFIRMATION.

## Read next
`client/memory/MEMORY.md` → `client/TODO.md` → `client/INDEX.md`

*Last updated: 2026-04-21*
