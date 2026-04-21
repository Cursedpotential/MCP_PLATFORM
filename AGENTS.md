# AGENTS.md — Root Redirect

> This file is a thin redirect. All behavioral rules live in the files below.
> Do not add rules here. If it belongs to a specific domain, it goes in that domain's AGENTS.md.

## Mandatory read order (every agent, every session)

```
Step 0:  git pull origin main
Step 1:  MCP_PLATFORM_SYSTEM_PROMPT_V3.md                        ← Full behavioral contract (THE LAW)
Step 2:  GROUND_TRUTH.md                                         ← Current platform state, component status
Step 3:  ORCHESTRATION_CONTRACT.md                               ← How agents, tools, CLIs are governed
Step 4:  memory/MEMORY.md                                        ← Last session log
Step 5:  memory/MATT.md                                          ← How Matt communicates and approves
Step 6:  INDEX.md                                                ← Navigate to your working directory
Step 7:  [workdir]/AGENTS.md                                     ← Domain rules for your working area
Step 8:  [workdir]/memory/MEMORY.md                              ← Domain session state
Step 9:  [workdir]/TODO.md                                       ← Approved tasks in your domain
Step 10: [workdir]/INDEX.md                                      ← What exists in your domain
```

### Conditional loads (read when relevant to your task)

```
Orchestration / workflow work:
  docs/wiki/skills/orchestration/conductor/SKILL.md              ← Conductor CLI, task types, workers, patterns

Conductor wiki reference:
  docs/wiki/skills/orchestration/conductor/OVERVIEW.md           ← ADR-033, CONDUCTOR GATE, open questions
  docs/wiki/skills/orchestration/conductor/OSS_REFERENCE.md      ← Task types, AI tasks, SDKs, CLI, Docker
  docs/wiki/skills/orchestration/conductor/PLATFORM_IMPLEMENTATION.md ← Worker patterns, HUMAN bridge (OQ-C5)
  docs/wiki/skills/orchestration/conductor/ECOSYSTEM.md          ← MCP server, Claude plugin, AI cookbook
```

Cascade inward. Each level's rules override the parent for that domain only.

## Domain AGENTS.md locations

| Domain | File |
|---|---|
| TS MCP Server | `mcp-servers/ts-mcp-server/AGENTS.md` |
| Py MCP Server | `mcp-servers/py-mcp-server/AGENTS.md` |
| JS MCP Server | `mcp-servers/js-mcp-server/AGENTS.md` |
| All MCP servers | `mcp-servers/AGENTS.md` |
| Infrastructure | `infrastructure/AGENTS.md` |
| React client | `client/AGENTS.md` |
| Documentation | `docs/AGENTS.md` |

## Approval language (non-negotiable)

`approved — proceed` = go. Everything else = not approval.

*Last updated: 2026-04-21*
