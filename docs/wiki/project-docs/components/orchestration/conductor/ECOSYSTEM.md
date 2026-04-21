---
title: Conductor — Ecosystem, Plugins & AI Cookbook
type: reference
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - mcp-server
  - plugins
  - ai-cookbook
  - tutorials
  - anti-gravity
  - claude
source_checked: 2026-04-21
---

# Conductor — Ecosystem, Plugins & AI Cookbook

## Official MCP Server

The `conductor-mcp` package exposes Conductor as a toolset for any MCP client (Claude Desktop, Cursor, Anti-Gravity, Claude Code).

### Install

```bash
pip install conductor-mcp
```

### Config File (`conductor-config.json`)

```json
{
  "CONDUCTOR_SERVER_URL": "https://developer.orkescloud.com/api",
  "CONDUCTOR_AUTH_KEY": "<YOUR_APPLICATION_AUTH_KEY>",
  "CONDUCTOR_AUTH_SECRET": "<YOUR_APPLICATION_SECRET_KEY>"
}
```

For local OSS server: `"CONDUCTOR_SERVER_URL": "http://localhost:8080/api"`

### Claude Desktop Integration

**macOS** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "conductor": {
      "command": "conductor-mcp",
      "args": ["--config", "/absolute/path/to/conductor-config.json"]
    }
  }
}
```

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "conductor": {
      "command": "conductor-mcp",
      "args": ["--config", "C:\\Users\\YourName\\conductor-config.json"]
    }
  }
}
```

Restart Claude after editing config. Verify in **Settings → Developer**.

### Cursor Integration

`Cursor → Settings → Cursor Settings → MCP → + Add new global MCP server` — same JSON config as Claude.

### GitHub AI Assistant / Codex Integration

```json
{
  "mcpServers": {
    "conductor": {
      "command": "uv",
      "args": [
        "--directory", "<ABSOLUTE_PATH_TO_CLONED_REPO>",
        "run", "conductor-mcp",
        "--config", "<ABSOLUTE_PATH_TO_CONFIG>"
      ]
    }
  }
}
```

### What the MCP Server Can Do

- Create workflow definitions from natural language
- Start workflow executions
- Monitor execution status
- Retrieve execution history and task results
- Analyze failed workflows and suggest fixes

### Source

- PyPI: https://pypi.org/project/conductor-mcp/
- GitHub: https://github.com/conductor-oss/conductor-mcp

---

## Claude Code Plugin

Install the official Conductor skills plugin for Claude Code:

```bash
/plugin marketplace add conductor-oss/conductor-skills
/plugin install conductor@conductor-skills
```

After install, Claude Code gains native Conductor workflow creation, execution, and management capabilities within the coding environment.

---

## Anti-Gravity Official MCP

Anti-Gravity IDE provides an official Conductor MCP server targeting both OSS and Orkes:

- **URL**: https://antigravity.codes/mcp/conductor
- Supports OSS (`http://localhost:8080/api`) and Orkes cloud endpoints
- Available in Anti-Gravity MCP marketplace

---

## Conductor Skills (Agent Upgrade)

Orkes maintains an official skill library for AI development agents. The user skill at `docs/wiki/skills/user/conductor/` is based on this. To upgrade:

```bash
# Linux/macOS
curl -sSL https://conductor-oss.github.io/conductor-skills/install.sh | bash -s -- --all --upgrade

# Windows (PowerShell)
irm https://conductor-oss.github.io/conductor-skills/install.ps1 -OutFile install.ps1; .\install.ps1 -All -Upgrade
```

---

## MCP Workbench

Interactive tool for building and testing Conductor + MCP integrations:

- GitHub: https://github.com/conductor-oss/mcp-workbench
- Provides a local sandbox for composing workflows that use MCP tool calls
- Test `LIST_MCP_TOOLS` + `CALL_MCP_TOOL` task patterns against real MCP servers

---

## AI Cookbook

The Conductor AI Cookbook covers LLM tasks, MCP tool calls, human approval workflows, dynamic forks, and durable agent execution patterns.

### Access

- Hosted docs: https://conductor-oss.github.io/conductor/index.html
- Examples repo: https://github.com/conductor-sdk/conductor-examples
- Go SDK examples: https://github.com/conductor-oss/go-sdk-examples

### Key Cookbook Patterns

#### 1. Basic AI Agent Loop (DO_WHILE + LLM_CHAT_COMPLETE)

Source: https://orkes.io/blog/building-a-basic-ai-agent-in-orkes-conductor/

```
DO_WHILE (cap: N iterations)
  LLM_CHAT_COMPLETE → strict JSON output: {action, tool, input, answer}
  SWITCH on action
    "TOOL"  → HTTP/CALL_MCP_TOOL → SET_VARIABLE → loop
    "FINAL" → TERMINATE with answer
```

Task types: `DO_WHILE`, `LLM_CHAT_COMPLETE`, `HTTP`, `SET_VARIABLE`, `SWITCH`, `TERMINATE`

Context injected into each LLM prompt:
- `Query: ${query}`
- `Iteration: ${iteration}`
- `Last action: ${last_action}`
- `Last tool: ${last_tool_name}`
- `Last tool result: ${last_tool_result}`
- `Conversation: ${messages}`

Design principles: explicit loop cap (safety), strict JSON from LLM (determinism), SET_VARIABLE for memory (no DB needed for short loops), SWITCH for routing (no code needed).

#### 2. Create Workflows from Natural Language (Claude + MCP)

Source: https://orkes.io/content/tutorials/create-workflows-using-ai-agent-claude

Use conductor-mcp in Claude Desktop. Claude:
1. Interprets natural language requirement
2. Generates JSON workflow definition
3. Registers definition via Conductor API
4. Executes it
5. Detects failures (e.g., JSON parsing errors in INLINE tasks), corrects, re-executes

Example prompt:
```
Create and execute a Conductor workflow named GetWeatherDubai. 
It should call a free public weather API that doesn't require an API key 
and return the current temperature in Dubai. Use schemaVersion 2.
```

#### 3. LangChain Agents in Production

Source: https://orkes.io/blog/how-to-orchestrate-langchain-agents-for-production-with-orkes-conductor/

Pattern: Wrap LangChain agents as Conductor SIMPLE task workers. Conductor handles:
- Retry and timeout
- Parallel execution (FORK_JOIN)
- Failure compensation (saga pattern)
- Human approval gates (HUMAN task)
- Full execution history for audit

#### 4. Human-in-the-Loop Approval

Pattern:
```
... processing tasks ...
HUMAN (taskRef: "analyst_review")
  → Pause until external signal
SWITCH on review_decision
  "approved"  → merge_to_production
  "rejected"  → archive_and_notify
```

Signal a HUMAN task from any HTTP client:
```bash
conductor task signal \
  --workflow-id {workflowId} \
  --task-ref analyst_review \
  --status COMPLETED \
  --output '{"decision": "approved", "analyst": "matts", "notes": "verified"}'
```

#### 5. Dynamic Fan-Out (FORK_JOIN_DYNAMIC)

Pattern for parallel ingestion across variable-length input lists:

```json
{
  "type": "FORK_JOIN_DYNAMIC",
  "name": "parallel_parse",
  "inputParameters": {
    "forkTaskName": "ts.parse.evidence",
    "forkTaskInputs": "${workflow.input.evidence_files}"
  }
}
```

One branch spawned per item in `evidence_files`. All branches run in parallel; JOIN waits for all.

#### 6. MCP Tool Calling from Workflows

```json
[
  {
    "type": "LIST_MCP_TOOLS",
    "name": "discover_tools",
    "inputParameters": {
      "server": "py-mcp-server"
    }
  },
  {
    "type": "CALL_MCP_TOOL",
    "name": "run_nlp",
    "inputParameters": {
      "server": "py-mcp-server",
      "tool": "semantica_extract_entities",
      "input": "${parse_task.output.text}"
    }
  }
]
```

---

## Tutorial Index

| Tutorial | URL | Task Types |
|----------|-----|------------|
| Create workflows with Claude (MCP) | https://orkes.io/content/tutorials/create-workflows-using-ai-agent-claude | INLINE, HTTP |
| Build a tiny AI agent | https://orkes.io/blog/building-a-basic-ai-agent-in-orkes-conductor/ | DO_WHILE, LLM_CHAT_COMPLETE, HTTP, SET_VARIABLE, SWITCH |
| LangChain agents in production | https://orkes.io/blog/how-to-orchestrate-langchain-agents-for-production-with-orkes-conductor/ | SIMPLE, FORK_JOIN, HUMAN |
| Agentic workflows (video) | https://www.youtube.com/watch?v=zsoTItNHdXw | — |

---

## Community & Examples

| Resource | URL |
|----------|-----|
| Conductor Examples Repo | https://github.com/conductor-sdk/conductor-examples |
| MCP Workbench | https://github.com/conductor-oss/mcp-workbench |
| Go SDK Examples | https://github.com/conductor-oss/go-sdk-examples |
| Conductor AGENTS.md | https://github.com/conductor-oss/conductor/blob/main/AGENTS.md |
| Orkes Blog | https://orkes.io/blog |
| Conductor OSS Org | https://github.com/conductor-oss |
