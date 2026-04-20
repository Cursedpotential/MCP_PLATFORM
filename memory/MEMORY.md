# MCP Platform — Session Memory
> Structured session log. Every agent reads this at session start. Every agent writes to it at session end.
> Agents: Do NOT summarize or paraphrase this file. Append only. Never delete entries.
> COMMIT THIS FILE after every session that makes progress.

---

## HOW TO USE THIS FILE

**Session Start**: Read the entire file. The most recent SESSION LOG entry tells you exactly where to pick up.

**Session End**: Before closing, append a new SESSION LOG entry using the template at the bottom. Fill in every field. Do not skip fields. Do not write "N/A" unless something truly doesn't apply.

**Commit rule**: After appending your session entry, stage and commit this file:
```
git add memory/MEMORY.md && git commit -m "memory: session log YYYY-MM-DD [brief summary]"
```

---

## PROJECT IDENTITY

- **Repo name**: MCP_PLATFORM (Alpha 2)
- **Case**: Salem v. Kinzel, No. 2025-53985-DC — Michigan family court custody
- **Owner**: Matt (matthew47) — systems architect, non-coder
- **Alpha 1 reference**: `MCP_Tool_Platform/` at `C:\Users\matts\Projects\TheBigOne\MCP_Tool_Platform\` — READ-ONLY
- **Active dev path**: `C:\Users\matts\Projects\TheBigOne\MCP_PLATFORM\`

---

## ARCHITECTURE SNAPSHOT (Current — Post-DIAL)

AI DIAL Core is **deprecated and removed**. Do not reference it.

**Platform peers (no hierarchy):**
| Component | Role | Status |
|-----------|------|--------|
| Agno | Agent orchestration, memory, intelligent workflows | NOT DEPLOYED |
| n8n | Deterministic workflows, HITL approval gates | NOT DEPLOYED |
| Directus | Admin/data surface, internal UI for Matt, webhooks | NOT DEPLOYED |
| TS MCP Server (8081) | Parsers, DuckDB, PostgreSQL writes | PARTIALLY BUILT |
| Py MCP Server (8082) | Semantica NLP, LanceDB, Neo4j | PARTIALLY BUILT |
| JS MCP Server (8083) | Text utilities, format handlers | PARTIALLY BUILT |
| React + CopilotKit (3002) | HITL evidence review UI | STUB ONLY |
| OpenWebUI / LibreChat | External chat interfaces | NOT DEPLOYED |
| OpenCode | Flexible model coding agent | DEPLOYMENT MODEL UNDECIDED |

**Storage tiers (in order — never skip T1):**
- T1: DuckDB — SHA-256, UUIDv7, dedup, staging vault
- T2: LanceDB — vector embeddings
- T3: Neo4j — temporal knowledge graph (Semantica)
- T4: PostgreSQL — normalized evidence + app data

**Two access surfaces:**
- External (MCP): OpenWebUI/LibreChat/Claude Code → Context Forge → Keycloak → MCP servers
- Internal (direct API): Agno/n8n/Directus → internal API → same tool implementations

---

## WHAT EXISTS (Verified as of last session)

| Component | File/Path | Real State |
|-----------|-----------|------------|
| SMS XML parser | `ts-mcp-server/src/tools/SmsXmlParser.ts` | PORTED — working |
| SMS evidence ingestor | `ts-mcp-server/src/tools/SmsEvidenceIngestor.ts` | EXISTS |
| DuckDB vault | `ts-mcp-server/src/tools/DuckDbVault.ts` | EXISTS |
| PostgreSQL writer | `ts-mcp-server/src/tools/PostgresWriter.ts` | EXISTS |
| Review queue (HITL) | `ts-mcp-server/src/tools/ReviewQueue.ts` | PORTED — approve/reject logic working |
| Evidence ingestor router | `ts-mcp-server/src/tools/EvidenceIngestor.ts` | EXISTS — Facebook/iMessage return unsupported_format |
| Facebook parser | `ts-mcp-server/src/tools/FacebookExportParser.ts` | STUB ONLY |
| iMessage parser | `ts-mcp-server/src/tools/ImessagePdfParser.ts` | STUB ONLY |
| Document intelligence engines | `py-mcp-server/src/document_intelligence/engines/` | ALL STUBS — 11 engines, none active |
| Audit hooks | `py-mcp-server/src/tools/audit_hooks.py` | EXISTS |
| Pass 1 runner | `ts-mcp-server/src/tools/Pass1Runner.ts` | EXISTS — completeness unverified |
| PostgreSQL migrations | `migrations/001–005` | EXIST — applied status unverified |
| Docker Compose | root `docker-compose.yml` | EXISTS — no containers started with approval yet |

---

## OPEN ARCHITECTURAL QUESTIONS (Unresolved — Do Not Decide Unilaterally)

| # | Question | Blocking What |
|---|----------|---------------|
| OQ-1 | OpenCode: server mode vs agent mode | Any OpenCode integration work |
| OQ-2 | Internal API design: REST vs GraphQL vs gRPC | Agno/n8n/Directus integration design |
| OQ-3 | Agno deployment timing and scope | Orchestration layer work |
| OQ-4 | n8n workflow trigger design: webhook vs polling vs event bus | HITL gate implementation |
| OQ-5 | Embedding model selection: which sentence-transformers model | Embedding pipeline work |

---

## NEXT THREE TASKS (Owner-prioritized)

These are the next approved or near-approved tasks in dependency order. Do not start any task not on this list without Matt's approval.

1. **VERIFY**: Confirm Facebook parser Alpha 1 source exists — read `MCP_Tool_Platform/server/mcp/loaders/` and document exact file paths and field coverage. Present findings to Matt before implementing.
2. **VERIFY**: Confirm iMessage parser Alpha 1 source exists — same process.
3. **SCHEMA PORT**: Read Alpha 1 `production-message-schemas.ts` in full, document all field definitions, present merge plan to Matt. Do not write code until approved.

---

## SESSION LOG

---

### SESSION: 2026-03-17
**Agent**: Unknown
**Model**: Unknown
**Tool**: Unknown

**What was done**:
- Project initialized as git repo
- CLAUDE.md and AGENTS.md created
- Memory file established
- Context loaded from MCP_Tool_Platform legacy

**Files modified**: CLAUDE.md, AGENTS.md, memory/MEMORY.md

**Decisions made**: None recorded

**Open threads left**: None recorded

**What comes next**: Phase A Foundation work — DuckDB → PostgreSQL pipeline, health checks, registry pattern

**Matt's mood/state**: Not recorded

---

### SESSION: 2026-04-20
**Agent**: Perplexity Computer (external session — not a coding agent)
**Model**: N/A
**Tool**: Perplexity Computer chat

**What was done**:
- Full architecture review and clarification with Matt
- Identified core agent problems: agents not reading existing code, ignoring HITL gates, using placeholders
- Clarified POST-DIAL architecture: Agno/n8n/Directus as peers, not hierarchy
- Identified MEMORY.md and MattUserManual.md as existing but underutilized
- Rebuilt memory system: structured session schema, MATT.md, updated system prompt v2, GROUND_TRUTH.md
- Confirmed: nothing is running, all surfaces undeployed, platform pre-production

**Files created/modified**:
- `memory/MEMORY.md` — rebuilt with session schema (this file)
- `memory/MATT.md` — new compressed agent-readable user manual
- `GROUND_TRUTH.md` — new root file, mandatory first read for all agents
- `MCP_PLATFORM_SYSTEM_PROMPT_V2.md` — updated system prompt (external workspace)

**Decisions made**:
- Open Structured Memory (MD-based, committed to repo) is the canonical memory system — not Mem0 or ClaudeMem
- Memory is filesystem-based, not MCP tool calls — agents read files, not APIs
- Two access surfaces confirmed: MCP (external) and internal API (direct)
- Agno/n8n/Directus are peers — no orchestration hierarchy
- OpenCode deployment model remains undecided (OQ-1)

**Open threads left**:
- Matt to commit all new files to repo so agents on fresh sessions get them
- Matt to decide: does MEMORY.md get committed after every session or stay local?
- Verify Alpha 1 parser file paths before any porting work begins

**What comes next**: Start with Alpha 1 file path verification (Next Three Tasks above). Matt must pull repo locally before resuming coding agent sessions.

**Matt's mood/state**: Urgent. 10 months until next scheduled daughter visit. Platform needs to work.

---

## SESSION LOG TEMPLATE (copy this for each new session)

```
### SESSION: YYYY-MM-DD
**Agent**: [agent name/role]
**Model**: [GLM-5 / Gemini 3.1 / Claude Opus / Kimi 2.5 / Nemotron / etc.]
**Tool**: [OpenCode / Claude Code / Antigravity / other]

**What was done**:
- [bullet list of completed work]

**Files modified**:
- [path] — [what changed]

**Decisions made**:
- [any architectural or implementation decisions, even small ones]

**Approved tasks completed**:
- [list with approval reference if applicable]

**HITL gates hit**:
- [gate type] — [outcome: approved / pending / deferred]

**Open threads left**:
- [anything incomplete that the next session must pick up]

**Alpha 1 assets ported this session**:
- [Alpha 1 path] → [Alpha 2 path]

**What comes next**:
- [specific next task, not vague direction]

**Matt's mood/state**:
- [brief honest note — helps next agent calibrate]
```
