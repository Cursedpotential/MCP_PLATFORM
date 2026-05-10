---
title: Conductor OSS — Engine Reference
type: reference
status: current
created: 2026-04-21
updated: 2026-04-21
reviewed: 2026-04-21
tags:
  - conductor
  - workflow-engine
  - task-types
  - ai-tasks
  - mcp
  - sdk
source: https://conductor-oss.github.io/conductor/
repo: https://github.com/conductor-oss/conductor
---

# Conductor OSS — Engine Reference

Source-grounded reference pulled from the Conductor OSS docs and GitHub. All features listed are confirmed present in the Apache 2.0 open-source release.

## Core Engine

### Durable Execution

- Workflow state persisted at every step
- Survives server restarts, worker crashes, network failures
- At-least-once task delivery with configurable retries
- Full execution history preserved indefinitely
- Replay any workflow from the beginning, from a specific task, or retry just the failed step — even months later

### Workflow Primitives

| Primitive | Description |
|-----------|-------------|
| `SIMPLE` | Calls a registered worker (polls task queue) |
| `HTTP` | Direct HTTP call — no worker needed |
| `INLINE` | JavaScript expression evaluated inline |
| `SWITCH` | Conditional branching on input or task output |
| `FORK_JOIN` | Static parallel branches — waits for all to complete |
| `FORK_JOIN_DYNAMIC` | Dynamic parallel branches — fan out over a list |
| `DO_WHILE` | Looping until condition met or cap hit |
| `SUB_WORKFLOW` | Inline execution of another workflow definition |
| `WAIT` | Pause until time elapsed, external signal, or webhook |
| `HUMAN` | Pause for human approval / manual input |
| `TERMINATE` | End workflow with explicit status and output |
| `SET_VARIABLE` | Write to workflow-scoped variables (in-memory state) |
| `JSON_JQ_TRANSFORM` | Transform task output using jq expressions |
| `EVENT` | Emit/consume events from message broker |

### AI / LLM Task Types

All confirmed in OSS (not enterprise-only):

| Task Type | Description |
|-----------|-------------|
| `LLM_CHAT_COMPLETE` | Call an LLM provider; supports system prompt, temperature, tools |
| `LLM_TEXT_COMPLETE` | Non-chat completion |
| `LIST_MCP_TOOLS` | Discover tools from an MCP server |
| `CALL_MCP_TOOL` | Execute a specific MCP tool |
| `LLM_GENERATE_EMBEDDINGS` | Generate vector embeddings |
| `LLM_INDEX_DOCUMENT` | Index document into vector store |
| `LLM_GET_EMBEDDINGS` | Retrieve embeddings from vector store |
| `LLM_SEARCH_INDEX` | Semantic similarity search over vector index |

### Supported LLM Providers (14+ native)

Anthropic · OpenAI · Azure OpenAI · Google Gemini · AWS Bedrock · Mistral · Cohere · HuggingFace · Ollama · and more.

### Vector Database Support (for RAG)

- Pinecone
- pgvector (PostgreSQL extension)
- MongoDB Atlas

### Infrastructure

| Component | Options |
|-----------|---------|
| Persistence | Redis, Postgres, MySQL, Cassandra, Dynamo — 5 backends |
| Message broker | Redis Streams, SQS, AMQP (RabbitMQ), Kafka, NATS, Conductor internal — 6 brokers |
| Server | JVM process, runs in Docker |
| Port | 8080 (UI + REST API) |

## CLI

```bash
npm install -g @conductor-oss/conductor-cli
conductor server start          # Start local server
conductor server status         # Check status
conductor workflow list         # List workflow definitions
conductor workflow get {name}   # Get definition
conductor workflow start -w {name} -i '{"key":"value"}'  # Run
conductor workflow search -s RUNNING -c 20               # Search executions
conductor task signal --workflow-id {id} --task-ref {ref} --status COMPLETED --output '{}'
```

## Docker

```bash
# Quickstart — server only
docker run -p 8080:8080 conductoross/conductor:latest

# Full stack with persistence (recommended)
git clone https://github.com/conductor-oss/conductor
cd conductor
docker compose -f docker/docker-compose.yaml up
```

UI available at `http://localhost:8080` after start.

## SDKs

| Language | Install |
|----------|---------|
| Python | `pip install conductor-python` |
| JavaScript / TypeScript | `npm install @io-orkes/conductor-javascript` |
| Java | `org.conductoross:conductor-client` (Maven/Gradle) |
| Go | `go get github.com/conductor-oss/conductor/conductor-go` |
| C# | NuGet `ConductorDotNetSDK` |
| Ruby | Gem `orkes-conductor-client` |
| Rust | Crates.io `conductor-client` |

All SDKs at: https://github.com/conductor-oss

## Worker Pattern

Workers are the execution units for `SIMPLE` tasks:

1. Worker polls Conductor server for tasks of a given type
2. Worker executes business logic
3. Worker reports result (COMPLETED or FAILED) with output payload
4. Conductor advances workflow to next step

Workers are:
- **Polyglot** — any language with an SDK
- **Idempotent** — Conductor may redeliver; workers must be safe to retry
- **Stateless** — state lives in the workflow; workers are ephemeral
- **Location-agnostic** — run anywhere Docker runs; poll outbound (no inbound firewall rules)

## Workflow Definition Schema

```json
{
  "name": "workflow_name",
  "description": "Human-readable description",
  "version": 1,
  "schemaVersion": 2,
  "tasks": [
    {
      "name": "task_name",
      "taskReferenceName": "task_ref",
      "type": "SIMPLE",
      "inputParameters": {
        "param": "${workflow.input.param}"
      }
    }
  ],
  "inputParameters": [],
  "outputParameters": {
    "result": "${task_ref.output.result}"
  },
  "failureWorkflow": "error_handler_workflow",
  "restartable": true,
  "workflowStatusListenerEnabled": false
}
```

See `docs/wiki/skills/user/conductor/references/workflow-definition.md` for the full schema.

## Execution States

`RUNNING` → `COMPLETED` | `FAILED` | `TIMED_OUT` | `TERMINATED` | `PAUSED`

Pause/resume, retry, restart, skip, and jump-to-task are all first-class operations.

## AGENTS.md

Conductor maintains a repo-level `AGENTS.md` for AI development agents:
https://github.com/conductor-oss/conductor/blob/main/AGENTS.md

## Official Sources

- Docs: https://conductor-oss.github.io/conductor/
- GitHub: https://github.com/conductor-oss/conductor
- Examples: https://github.com/conductor-sdk/conductor-examples
- MCP Workbench: https://github.com/conductor-oss/mcp-workbench
- Go SDK Examples: https://github.com/conductor-oss/go-sdk-examples
