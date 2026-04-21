# MCP Platform — Root Agent Index
> Start here. Every agent. Every session.
> Read GROUND_TRUTH.md first, then use this file to navigate.

---

## I need to know the current platform state
→ `GROUND_TRUTH.md` — what runs, what doesn't, open questions, approved tasks

## I need to know the rules for all agents
→ `AGENTS.md` — universal agent rules, roles, coordination patterns

## I need to know where the last session left off
→ `memory/MEMORY.md` — session log
→ `memory/MATT.md` — how Matt works and what he expects

## I need to know what tasks are approved to work on
→ `TODO.md` — platform-level tasks and phase gates
→ `[workdir]/TODO.md` — domain-specific approved tasks

## I need to work on parsers or storage (TypeScript)
→ `mcp-servers/ts-mcp-server/` — see local AGENTS.md + TODO.md + INDEX.md

## I need to work on NLP, embeddings, or graph (Python)
→ `mcp-servers/py-mcp-server/` — see local AGENTS.md + TODO.md + INDEX.md

## I need to work on text utilities (JavaScript)
→ `mcp-servers/js-mcp-server/` — see local AGENTS.md + TODO.md + INDEX.md

## I need to work on Docker, Keycloak, Caddy, or databases
→ `infrastructure/` — see local AGENTS.md + TODO.md + INDEX.md

## I need to work on the React UI or CopilotKit
→ `client/` — see local AGENTS.md + TODO.md + INDEX.md

## I need to find something in Alpha 1 (read-only reference)
→ `docs/wiki/alpha1-inventory.md` — full catalog (produced by documentation agent)
→ Alpha 1 local path: `C:\Users\matts\Projects\TheBigOne\MCP_Tool_Platform\`

## I need architecture documentation
→ `docs/wiki/architecture/` — overview, storage tiers, chain of custody, MCP server roles

## I need tool reference documentation
→ `docs/wiki/tools/INDEX.md` — all MCP tools, inputs/outputs, status

## I need workflow documentation
→ `docs/wiki/workflows/` — ingestion, HITL review, Pass 1 analysis

## I need to understand a decision that was made
→ `DECISION_REGISTER.md` — ADR-001 through ADR-032

## I need to write a spec before implementing
→ `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md` — how to write specs
→ `docs/specs/` — existing specs

## I need to check what's in the wiki
→ `docs/wiki/README.md` — wiki master index (produced by documentation agent)

## I need the system prompt to paste into a new agent session
→ `MCP_PLATFORM_SYSTEM_PROMPT_V3.md` ← current
→ ~~`_DEPRECATED/MCP_PLATFORM_SYSTEM_PROMPT_V2.md`~~ — deprecated 2026-04-21

---

## Key File Reference

| File | Purpose | Must Read |
|------|---------|-----------|
| `GROUND_TRUTH.md` | Platform state | YES — first |
| `AGENTS.md` | Universal rules | YES — second |
| `memory/MEMORY.md` | Session log | YES — third |
| `memory/MATT.md` | Matt reference | YES — fourth |
| `TODO.md` | Platform tasks | YES — before starting work |
| `MCP_PLATFORM_SYSTEM_PROMPT_V3.md` | System prompt — current | Paste into agent |
| ~~`_DEPRECATED/MCP_PLATFORM_SYSTEM_PROMPT_V2.md`~~ | ~~System prompt~~ | ⛔ Deprecated — use V3 |
| `ORCHESTRATION_CONTRACT.md` | Agent governance | How agents/tools/CLIs are governed |
| `DECISION_REGISTER.md` | ADR log | When making/checking decisions |
| ~~`_DEPRECATED/AGENT_HANDOFF_PROMPT_POST_DIAL.md`~~ | ~~Handoff context~~ | ⛔ Deprecated — use ORCHESTRATION_CONTRACT.md |
| `PARITY_MATRIX.md` | Feature status | When checking what's built — verify against GROUND_TRUTH.md |
| `docs/wiki/alpha1-inventory.md` | Alpha 1 asset catalog | Before porting anything |
