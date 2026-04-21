# GROUND TRUTH — MCP Platform
> READ THIS FIRST. Every agent. Every session. No exceptions.
> Last updated: 2026-04-20 | Updated by: Matt (owner)

---

## THE SITUATION

This is a forensic evidence platform supporting active custody litigation (Salem v. Kinzel).
Nothing is in production. Nothing is running. The goal is to get it running — correctly, in order.

**Matt is the only human on this project. He is not a coder. He sets direction. You execute.**

---

## PLATFORM COMPONENTS (Peers — No Hierarchy)

| Component | Role | Status |
|-----------|------|--------|
| **Agno** | Agent orchestration, memory, dynamic tool calling, intelligent workflows | NOT DEPLOYED — future glue |
| **n8n** | Deterministic workflows, visual flows, HITL approval gates | NOT DEPLOYED |
| **Directus** | Admin/data surface, webhook triggers, internal UI for Matt | NOT DEPLOYED |
| **TS MCP Server** (port 8081) | Parsers, DuckDB vault, PostgreSQL writes | PARTIALLY BUILT |
| **Py MCP Server** (port 8082) | Semantica NLP, LanceDB, Neo4j | PARTIALLY BUILT |
| **JS MCP Server** (port 8083) | Text utilities, format handlers | PARTIALLY BUILT |
| **React + CopilotKit** (port 3002/5173) | HITL evidence review UI | STUB ONLY |
| **OpenWebUI / LibreChat** | External chat interfaces | NOT DEPLOYED — planned |
| **OpenCode** | Flexible model coding agent | DEPLOYMENT MODEL UNDECIDED — do not assume |
| **Keycloak** (port 8180) | OIDC/JWT auth | EXISTS IN DOCKER COMPOSE |
| **WunderGraph Cosmo** (port 4000) | GraphQL federation | EXISTS IN DOCKER COMPOSE |
| **Caddy** | HTTPS proxy/routing | EXISTS IN CONFIG |

**Two access surfaces exist:**
- **MCP surface** — External tools (OpenWebUI, LibreChat, Claude Code, OpenCode) connect via MCP protocol through Context Forge + Keycloak
- **Internal surface** — Agno, n8n, Directus connect directly to internal APIs without MCP hop

**Internal API must be designed as the canonical interface. MCP tools are thin wrappers over it.**

---

## WHAT ACTUALLY EXISTS AND RUNS TODAY

| What | Where | State |
|------|-------|-------|
| SMS XML parser | `ts-mcp-server/src/tools/SmsXmlParser.ts` | PORTED — verify before touching |
| SMS evidence ingestor | `ts-mcp-server/src/tools/SmsEvidenceIngestor.ts` | EXISTS |
| DuckDB vault | `ts-mcp-server/src/tools/DuckDbVault.ts` | EXISTS |
| PostgreSQL writer | `ts-mcp-server/src/tools/PostgresWriter.ts` | EXISTS |
| Review queue | `ts-mcp-server/src/tools/ReviewQueue.ts` | EXISTS — HITL approve/reject logic |
| Evidence ingestor router | `ts-mcp-server/src/tools/EvidenceIngestor.ts` | EXISTS — Facebook/iMessage return unsupported |
| Facebook parser | `ts-mcp-server/src/tools/FacebookExportParser.ts` | STUB ONLY |
| iMessage parser | `ts-mcp-server/src/tools/ImessagePdfParser.ts` | STUB ONLY |
| Document intelligence engines | `py-mcp-server/src/document_intelligence/engines/` | STUBS ONLY — 11 engines, none active |
| Audit hooks | `py-mcp-server/src/tools/audit_hooks.py` | EXISTS |
| Pass 1 runner | `ts-mcp-server/src/tools/Pass1Runner.ts` | EXISTS — verify completeness |
| PostgreSQL migrations | `migrations/001–005` | EXIST — verify applied |

**Nothing is running. Docker Compose exists but no containers have been started with owner approval.**

---

## ALPHA 1 — READ-ONLY REFERENCE (DO NOT MODIFY)

Alpha 1 repo: `MCP_Tool_Platform/` (local path: `C:\Users\matts\Projects\TheBigOne\MCP_Tool_Platform\`)

**Before writing any new implementation, search Alpha 1 first.**

| Alpha 1 Asset | Location | Alpha 2 Action |
|--------------|----------|----------------|
| Messaging schemas | `server/mcp/loaders/production-message-schemas.ts` | PORT + MERGE (add Alpha 2 fields, never replace Alpha 1 fields) |
| Pattern analyzer | `server/mcp/analysis/` | PORT to py-mcp-server |
| Chain of custody | `server/mcp/custody/` | PORT to ts-mcp-server |
| Evidence hasher | `server/mcp/hasher/` | PORT to ts-mcp-server |
| HurtLex NLP | `server/mcp/nlp/` | PORT to py-mcp-server |
| Review queue | `server/mcp/review/` | ALREADY PORTED — verify parity |
| Evidence registry | `server/mcp/registry/` | PORT to ts-mcp-server |
| Facebook parser | `server/mcp/loaders/` | PORT to FacebookExportParser.ts |
| iMessage parser | `server/mcp/loaders/` | PORT to ImessagePdfParser.ts |

> Verify actual file paths by reading Alpha 1 directly. This table is a guide, not a guarantee.

---

## WHAT NEEDS TO HAPPEN (IN ORDER)

These are the three outcomes that matter for the case, in dependency order:

### Outcome 1: INGEST (Most Urgent)
Files go in → SHA-256 hash at first touch → chain of custody established → messages normalized and stored.

Required to reach this:
1. Facebook parser: STUB → working (port from Alpha 1)
2. iMessage parser: STUB → working (port from Alpha 1)
3. Messaging schemas: port `production-message-schemas.ts` from Alpha 1, merge Alpha 2 extensions
4. DuckDB → PostgreSQL pipeline: verify end-to-end
5. Docker containers: start with owner approval, in order

### Outcome 2: SEARCH
Ingested evidence is searchable semantically and by keyword.

Required to reach this:
1. Ingest working (Outcome 1)
2. Embedding service in py-mcp-server (sentence-transformers, local)
3. LanceDB write path wired to post-parse pipeline
4. `evidence_search` MCP tool registered

### Outcome 3: OUTPUT
Evidence generates court-ready documents, timelines, reports.

Required to reach this:
1. Search working (Outcome 2)
2. Pass 1 analysis pipeline (port sentiment/HurtLex from Alpha 1)
3. Document intelligence engines (Pandoc + Tesseract first, local only)
4. Directus activated for data surface access

---

## OPEN ARCHITECTURAL QUESTIONS (DO NOT RESOLVE WITHOUT MATT)

These are undecided. Agents must NOT make assumptions or implement solutions for these:

| Question | Why It Matters |
|----------|----------------|
| OpenCode deployment: server mode vs agent mode | Affects how coding agents are invoked and how model switching works |
| Internal API design: REST vs GraphQL vs gRPC | Determines how Agno/n8n/Directus connect to tool implementations |
| Agno deployment: when and how to introduce it | Agno is the future orchestration glue — premature deployment creates dependency debt |
| n8n workflow triggers: webhook vs polling vs event bus | Affects how HITL gates are implemented in practice |
| Embedding model selection: which sentence-transformers model | Affects search quality and local resource requirements |
| Planner agent design | Conductor executes; something must decide which workflow to run. Agno was the planned planner. No replacement decided. Gated behind first Conductor workflow running end-to-end. |
| /api/chat endpoint design | Needs to route: plain LLM (LiteLLM), tool calls (ContextForge MCP), workflow control (Conductor). Request/response schema not yet defined. |
| Conductor HUMAN task ↔ ReviewQueue bridge | When a Conductor HUMAN task fires, it must sync with `app.review_queue` and notify the UI. Mechanism not yet designed. |

When you encounter one of these in implementation, STOP. Flag it. Ask Matt. Do not decide unilaterally.

---

## SEMANTICA

Semantica is a pivotal component of the forensic intelligence layer. It is the NLP/AI engine for:
- Named entity extraction (`semantica_extract_entities`)
- Knowledge graph construction (`semantica_build_graph`)
- Temporal fact extraction (`semantica_extract_temporal_facts`)
- Conflict/contradiction detection (`semantica_detect_conflicts`)
- Embedding generation (`semantica_generate_embeddings`)
- Evidence provenance tracking (`semantica_track_provenance`)

Semantica tools live in `py-mcp-server`. They are called by the TS server (Pass1Runner) and will be called by Conductor workers.

**Rule for agents**: Treat Semantica tools as authoritative. Do not rewrite their interfaces. Do not stub their implementations. If a Semantica tool is missing or broken, flag it — do not work around it.

---

## UNKNOWN COMPONENTS

This platform contains more components, tools, and integrations than any single document captures. When an agent encounters a reference to an unknown component:

1. STOP
2. Emit: `UNKNOWN_COMPONENT: [name] — encountered at [file:line]. No documentation found.`
3. Ask Matt. Do not assume. Do not infer. Do not implement.

---

## ABSOLUTE RULES (NO EXCEPTIONS)

1. **Read Alpha 1 before writing anything new.** If it exists there, port it. Never rewrite from scratch.
2. **Do not touch working code** unless fixing a bug you directly introduced.
3. **No placeholders.** No TODOs. No `pass`. No `throw new Error("not implemented")`. Implement it or explicitly defer with owner approval.
4. **No container starts** without Matt saying "approved — proceed" naming the specific service.
5. **No cloud API wiring** (Google DocAI, AWS Textract, LlamaParse, IBM watsonx) without explicit approval naming the engine.
6. **No schema changes** without a numbered migration file (`migrations/00N_description.sql`).
7. **No secrets hardcoded.** Everything goes in `.env`.
8. **Run `scripts/git/prepush-check.sh` before every push.**
9. **OpenCode deployment model is undecided.** Do not implement any OpenCode integration until Matt decides.

---

## APPROVAL LANGUAGE

| Matt says | Meaning |
|-----------|---------|
| "approved — proceed" | ✅ Go. Execute the exact plan submitted. |
| "looks good" / "sounds right" / "yes" / silence | ❌ NOT approval. Ask again with the exact task name. |

---

## MANDATORY READ ORDER (Every Agent, Every Session)

```
Step 0:  git pull origin main               ← sync before reading anything
Step 1:  GROUND_TRUTH.md                   ← this file — platform state
Step 2:  AGENTS.md                          ← universal rules
Step 3:  memory/MEMORY.md                  ← session log, last state
Step 4:  memory/MATT.md                    ← how Matt works
Step 5:  [workdir]/AGENTS.md               ← local domain rules
Step 6:  [workdir]/memory/MEMORY.md        ← local domain state
Step 7:  [workdir]/TODO.md                 ← approved tasks in this area
Step 8:  [workdir]/INDEX.md                ← where to find things here
```

After reading all 8, emit the session start block (see system prompt).
Do not write any code until Matt gives a specific task and says "approved — proceed."

---

## HOW TO END A SESSION

```
Step 1:  Update [workdir]/TODO.md status for completed/in-progress tasks
Step 2:  Append to [workdir]/memory/MEMORY.md using the session template
Step 3:  Append to memory/MEMORY.md (root) if platform-level decisions were made
Step 4:  git add memory/ [workdir]/memory/ [workdir]/TODO.md
Step 5:  git commit -m "memory: session log YYYY-MM-DD — [one line summary]"
Step 6:  scripts/git/prepush-check.sh
Step 7:  git push origin main
Step 8:  Emit SESSION END block (see system prompt)
```

---

## HOW TO START A SESSION

1. Read this file (`GROUND_TRUTH.md`)
2. Read `AGENTS.md`
3. Read the `AGENTS.md` in the subdirectory you are working in
4. State out loud: what you read, what phase you understand you're in, what specific task Matt has given you
5. If Matt has NOT given you a specific task yet, ask: "What are we working on today?"
6. Do not generate any code until you have completed steps 1–5 and have an explicit approved task

---

## DEPRECATED STALE PLANNING DOCUMENTS

> The following documents were written before DIAL Core deprecation and the Conductor OSS pivot (ADR-033).
> They contain architectural references that are now incorrect. **GROUND_TRUTH.md supersedes all of them.**
> Do NOT update these docs. Do NOT follow rules in them that conflict with GROUND_TRUTH.md.
> They are preserved for historical reference only.

| Stale Document | What's Wrong |
|---|---|
| `POST_DIAL_MASTER_OVERVIEW.md` | References DIAL Core as operational |
| `SPRINT_PLAN.md` | References Agno and n8n as future components; references DIAL Core |
| `POST_DIAL_REPLACEMENT_ARCHITECTURE.md` | References Agno and n8n in replacement architecture; references DIAL Core as gateway |
| `IMPLEMENTATION_PHASE_PLAN.md` | May reference Agno/n8n deployment phases; treat as stale |
| `AGENT_HANDOFF_PROMPT_POST_DIAL.md` | Written post-DIAL but pre-Conductor; Agno/n8n references are stale |
