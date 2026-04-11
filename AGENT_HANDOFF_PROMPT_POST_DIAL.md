# Agent Handoff Prompt — Post-DIAL MCP Platform

---

> 🚨 **CRITICAL NOTICE — READ BEFORE DOING ANYTHING**
>
> This document is a **PLANNING FRAMEWORK**, not permission to implement.
>
> **Every phase, every major task, every architectural decision requires explicit owner approval before any code is written, any service is activated, or any configuration is changed.**
>
> Presenting a plan and receiving the response "looks good" is NOT approval to execute. You must receive an unambiguous "approved — proceed" from the owner before touching any code or configuration.
>
> If you are uncertain whether you have approval, **stop and ask**.

---

## Context

You are taking over development of the **MCP Platform** — a forensic evidence processing system built on:

- **DIAL Core** (port 8080) — AI gateway and MCP tool dispatcher
- **Three MCP servers**: TypeScript (8081), Python (8082), JavaScript (8083)
- **Storage tiers**: DuckDB (fingerprint vault), PostgreSQL (evidence store), LanceDB (vector embeddings), Neo4j (knowledge graph)
- **Auth**: Keycloak OIDC/JWT
- **Routing**: Caddy HTTPS proxy
- **GraphQL**: WunderGraph Cosmo federation
- **UI**: CopilotKit React (HITL review), DIAL Chat, Directus (data surface — pending activation), OpenWebUI + LibreChat (planned)

**Alpha 1** codebase lives in `MCP_Tool_Platform/` — it is read-only reference material containing proven implementations you must port from rather than rewrite.

---

## Hard Rules

### Rule 1: Alpha 1 First
Before writing any new implementation code, search `MCP_Tool_Platform/` for an existing Alpha 1 implementation. If one exists:
- Read it fully
- Port it to Alpha 2
- Do not rewrite it from scratch
- Do not modify the Alpha 1 source files

Applicable Alpha 1 assets include (but are not limited to): pattern analyzer, chain of custody module, evidence hasher, HurtLex integration, review queue logic, registry, and messaging schemas.

### Rule 2: Never Modify Existing Working Code
If a component is working correctly, do not modify it unless you are fixing a bug that was directly introduced by your own changes. Do not "clean up," "refactor," or "improve" working code without explicit owner approval.

### Rule 3: Messaging Schemas — Port from Alpha 1 production-message-schemas.ts
All messaging parser schema work (SMS, Facebook, iMessage) starts from `production-message-schemas.ts` in Alpha 1. The correct approach is:
1. Read Alpha 1 `production-message-schemas.ts` in full
2. Document all field definitions
3. Merge Alpha 2 additions: pgvector embedding fields, `device_id` tracking, WAL-compatible columns
4. Write the merged schema
5. Do not replace Alpha 1 field definitions — only add Alpha 2 extensions

### Rule 4: HITL Gates Are Real — Stop and Wait
Every development phase ends with a STOP gate requiring owner approval before the next phase begins. These gates are not formalities. Do not:
- "Just start" the next phase while waiting for approval
- Interpret silence as approval
- Begin implementation of "obviously necessary" tasks without explicit approval

When you reach a gate: present your outputs, state clearly that you are waiting for approval, and stop.

### Rule 5: Plan Before You Code
Before writing any implementation code, write a spec document in `docs/specs/` describing:
- What you plan to implement
- Which Alpha 1 assets you will port
- What new code is required
- What tests you will write
- What the success criteria are

Present the spec to the owner. Wait for explicit approval before writing implementation code.

### Rule 6: "Approved in Principle" ≠ "Approved for Execution"
A statement like "yes, we should eventually do X" or "that sounds right" is not approval to execute. Approval must be explicit: "approved — implement task X as described in spec Y."

### Rule 7: Cloud Engines Require Explicit Activation Approval
The document intelligence router supports 11 engines. Cloud engines (Google DocAI, AWS Textract, LlamaParse, IBM watsonx) must never be activated without a specific, documented owner approval that names the engine and confirms that credentials may be wired. The presence of an interface stub or placeholder configuration does NOT constitute approval to activate.

---

## Alpha 1 Asset Inventory

| Asset | Location in Alpha 1 | Alpha 2 Action |
|-------|---------------------|----------------|
| Pattern analyzer (sentiment, intent) | `MCP_Tool_Platform/server/mcp/analysis/` | Port to py-mcp-server |
| Chain of custody module | `MCP_Tool_Platform/server/mcp/custody/` | Port to ts-mcp-server |
| Evidence hasher (SHA-256 CLI) | `MCP_Tool_Platform/server/mcp/hasher/` | Port to ts-mcp-server |
| HurtLex integration | `MCP_Tool_Platform/server/mcp/nlp/` | Port to py-mcp-server |
| Review queue logic | `MCP_Tool_Platform/server/mcp/review/` | Port to ts-mcp-server |
| Evidence registry | `MCP_Tool_Platform/server/mcp/registry/` | Port to ts-mcp-server |
| Messaging schemas | `MCP_Tool_Platform/server/mcp/loaders/production-message-schemas.ts` | Port + merge Alpha 2 extensions |
| SMS parser | `MCP_Tool_Platform/server/mcp/loaders/` | Already ported to Alpha 2; use as reference |
| Facebook parser (Alpha 1) | `MCP_Tool_Platform/server/mcp/loaders/` | Port to Alpha 2 stub |
| iMessage parser (Alpha 1) | `MCP_Tool_Platform/server/mcp/loaders/` | Port to Alpha 2 stub |

> **Before taking any of the above actions**, verify the actual file paths by reading `MCP_Tool_Platform/` directly. This table is a guide, not a guarantee of current file locations.

---

## Immediate Priorities (With Approval Gates)

These are the highest-priority tasks in Phase 1. Each requires owner approval before execution.

### Priority 1: Directus Activation
- **What**: Activate Directus as the user-facing data/admin surface
- **Where**: `docker-compose.yml` (service already defined)
- **What needs approval**: Starting the container, configuring PostgreSQL connection, setting up RBAC
- **Gate**: Owner must explicitly approve before `docker compose up directus` is run

### Priority 2: Document Intelligence Local Engines (Pandoc, Tesseract)
- **What**: Implement Pandoc (format conversion) and Tesseract (OCR) as working local engines in the document intelligence router
- **Where**: `mcp-servers/py-mcp-server/src/` and/or `mcp-servers/ts-mcp-server/src/`
- **What needs approval**: `EngineRouter` interface design + each engine implementation
- **Gate**: Owner must review the interface design spec before any implementation begins

### Priority 3: Messaging Schema Port
- **What**: Port `production-message-schemas.ts` from Alpha 1, merge Alpha 2 extensions
- **Where**: `mcp-servers/ts-mcp-server/src/`
- **What needs approval**: The merged schema document (present as a spec, not code, first)
- **Gate**: Owner must review merged schema before any PostgreSQL migrations are written

### Priority 4: CopilotKit React Chat Module Wiring
- **What**: Complete integration of the CopilotKit React module in `client/`
- **Where**: `client/`
- **What needs approval**: UI interaction design, tool call mapping, state management approach
- **Gate**: Owner must review the integration spec before any `client/` changes

### Priority 5: OpenWebUI + LibreChat as Remote Chat Interfaces
- **What**: Add docker-compose service definitions for OpenWebUI and LibreChat, configure DIAL Core routing, register Keycloak clients
- **Where**: `docker-compose.yml`, Keycloak admin, Caddy config
- **What needs approval**: Both services require individual owner approval before activation
- **Gate**: Owner must explicitly approve each service individually. Do not start containers until approved

---

## What NOT To Do

The following actions are **forbidden** without explicit owner approval:

| Forbidden Action | Why |
|-----------------|-----|
| Modify any file in `MCP_Tool_Platform/` | Alpha 1 is read-only reference material |
| Start any new Docker container | Requires owner approval |
| Wire any cloud API credentials (Google, AWS, IBM, LlamaCloud) | Cloud activation approval required |
| Write Pass 1 records to production | WORM — once written, immutable |
| Change PostgreSQL schema without a migration script | Data integrity risk |
| Expose any service on a public port without Keycloak | Security violation |
| Begin Phase N+1 without Phase N gate approval | Process violation |
| Interpret "sounds good" as approval to implement | Approval must be explicit |
| "Refactor" or "clean up" working code | Risks breaking working functionality |
| Hardcode secrets or credentials in any file | Security violation; also caught by pre-push scan |
| Skip `scripts/git/prepush-check.sh` before pushing | Secret scan bypass |
| Delete or archive documentation without owner review | Documentation chain of custody |

---

## Key Reference Documents

| Document | Purpose |
|----------|---------|
| `AGENTS.md` | Root instruction file for all agents — read first |
| `docs/INDEX.md` | Live documentation entrypoint |
| `POST_DIAL_MASTER_OVERVIEW.md` | Platform vision, strategic direction, hard rules |
| `POST_DIAL_REPLACEMENT_ARCHITECTURE.md` | Component responsibility matrix, data flow |
| `IMPLEMENTATION_PHASE_PLAN.md` | Phased tasks with complexity and approval gates |
| `SPRINT_PLAN.md` | Detailed block-by-block task breakdown |
| `PARITY_MATRIX.md` | Feature-by-feature status inventory |
| `MIGRATION_DECISIONS.md` | Per-capability migration decisions and rationale |
| `DECISION_REGISTER_POST_DIAL.md` | ADR log (ADR-001 through ADR-026) |
| `docs/architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md` | Multi-engine document intelligence design |
| `docs/specs/SPEC_DRIVEN_DEVELOPMENT.md` | How to write and submit specs for approval |
| `docs/plans/ROADMAP.md` | Current-state roadmap |

---

## Approval Request Template

When you are ready to request owner approval for a task or phase, present your request in this format:

```
## Approval Request

**Task/Phase**: [name and ID]
**Spec document**: [link to docs/specs/ document]
**What I will do**: [concise description of implementation steps]
**What I will NOT do**: [explicitly state what is out of scope]
**Alpha 1 assets being ported**: [list, or "none"]
**Tests planned**: [list of test cases]
**Rollback plan**: [how to undo if something goes wrong]
**Expected outputs**: [what will exist when this task is complete]

Requesting approval to proceed.
```

Do not begin implementation until you receive an explicit "approved — proceed" response.

---

## Environment Notes

- **Git identity**: Use WSL git for pushes. Verify auth before pushing: `GIT_SSH_COMMAND="ssh -i /home/matts/.ssh/id_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes" git ls-remote origin -h refs/heads/main`
- **Pre-push scan**: Run `scripts/git/prepush-check.sh` before every push to catch secrets
- **No /tmp**: Never write to `/tmp`. All intermediate files go in the project directory
- **Secrets**: Never hardcode credentials. Use `.env` files (which are in `.gitignore`)
- **Databases**: Use lazy initialization for all database connections

---

*Last updated: see git log*
