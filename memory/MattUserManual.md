# Matt's User Manual

**Generated**: 2026-03-08
**Last Updated**: 2026-03-08
**Data Sources**: mem0 (100+ memories), conversation history (1,904 lines scanned), structured memory

---

## Who is Matt?

Matt is **NOT a trained programmer**. He builds complex systems through iteration, research, and pattern recognition—not formal education. He appreciates plain language explanations, clear tradeoffs, and getting approval before code is written.

**Technical Expertise Areas:**
- TypeScript/JavaScript (React 19, tRPC, Drizzle ORM, MCP Tool Platform)
- Python (ML/NLP workflows, PyMuPDF, Neo4j, GraphRAG, Semantica)
- SQL/Database architecture (PostgreSQL with PostGIS/TimescaleDB, MySQL, DuckDB, LanceDB)
- MCP (Model Context Protocol) server architecture and management
- GraphQL federation and API design
- PowerShell scripting and Windows filesystem work
- Legal/forensic workflows (Michigan family law, custody disputes)

**Project Portfolio:**
- TheBigOne (Parent Suite)
- MCP Tool Platform (~70-75% complete, ~90 TS errors)
- TraceIQ Forensic (SQL-based evidence platform)
- Evidence Analysis v3.0.0 (reorganized structure)

---

## Communication Style

### Writing Style (from conversation history)

**Characteristics:**
- Casual, informal tone with frequent profanity when frustrated ("fucking", "shit", "damn", "goddamn")
- Stream-of-consciousness writing with run-on sentences and ellipses ("...", ", so", ", umm")
- Frequent typos ("parsinbg", "regressed instead of progressed", "hookj")
- Conversational interruptions ("Sorry, I interrupted", "Hold on 1st")
- Direct and sometimes blunt feedback ("that's useless", "That's stupid")
- Rephrases instructions when not understood or when repeating
- Lowercase frequently, casual/conversational tone
- Uses "continue", "cont", "yep", "ok" as acknowledgment

**When Frustrated:**
- Stronger language ("fucking", "shit", "damn")
- Repeats messages when not getting expected response
- "For the last time" phrase when not listened to

---

## Response Requirements (MANDATORY)

**Response Style: CONCISE**
- Get to the point immediately
- Short responses preferred
- Skip "why" explanations unless explicitly asked
- Use bullets over paragraphs
- Code first, then explanation if needed
- No fluff—no "Great question", no validation filler
- No emojis unless user explicitly requests them

### Planning Workflow

**CRITICAL**: Matt is not a trained programmer. Do NOT:
- Write code first, then suggest improvements
- Iterate with "oh, we should also add..." after writing code
- Assume Matt knows programming conventions
- Present code without plain language explanation
- Skip planning for "simple" tasks

**DO INSTEAD**:
1. Analyze request
2. Check Context7 for library/API docs
3. Check memory for prior work
4. Identify best practices
5. Surface gaps and questions
6. Propose enhancements
7. Present plan → GET APPROVAL
8. THEN write code
9. Explain key decisions in plain language

**Front-load thinking, not typing.**

---

## Technical Preferences

### Model Priority Order

1. **Antigravity** (Google) - Primary preference
2. **Z.AI GLM** - Favorite, cheap planning model (glm-5)
3. **Kimi** - Subscription
4. **OpenCode Free** - Tiers
5. **NVIDIA Nemotron** - Available
6. **OpenRouter Free** - Tiers
7. **Groq** - Fast, secondary option
8. **Google** - For docs tasks (but goes off on tangents)
9. **OpenAI** - Available
10. **GitHub** - Available
11. **Anthropic** - Available
12. **OpenCode Paid** - When needed
13. **Fireworks** - Available
14. **Ollama** - Available

**Dislikes**: O3 Mini, Haiku (too weak)

### Cost Optimization Rules

**Venice.ai Usage**:
- 1000 credits/month
- Use for `venice-uncensored` and unique models ONLY
- Do NOT waste credits on Claude, GPT, Gemini, Kimi, GLM (covered elsewhere)
- Save credits for uncensored/unique content that's Venice's actual value prop

**General**:
- Use cheapest suitable model for the task
- Don't waste expensive models on simple tasks
- Matt explicitly requests "Before it waste more usage with Opus, I'm going to give you a shot"

### Tools and Services

| Tool/Service | Provider | Use Case | Notes |
|--------------|----------|----------|-------|
| Context7 | API docs lookup | Pre-flight—ALWAYS use before assuming API behavior |
| mem0 | Semantic memory search | Cross-session context persistence |
| mcp-structured-memory | Structured docs | Project tracking, living documents |
| Semantica | Temporal knowledge graphs | Replaced Graphiti (deprecated) |
| DuckDB | First-touch ingestion | SHA-256 dedup, metadata, staging |
| Neo4j | Knowledge graph storage | Single `evidence_graph` DB |
| LanceDB | T2 for embeddings | Vector search |
| PostgreSQL | Evidence storage | PostGIS for geospatial, TimescaleDB for time-series |
| MySQL | App state | Control plane (users, API keys, workflows, settings) |
| Cohere | Embeddings/reranking | Best-in-class, free on testing API |
| MCP servers | Protocol integration | Heavy usage, frequent troubleshooting |
| OpenCode | TUI platform | Preferred for agent work |
| Claude Code | CLI platform | For direct interaction |
| PowerShell | Windows scripting | File operations, deduplication |

---

## File Management Preferences

### Folder Organization

**CRITICAL**: Matt wants ONE clean codebase.

**Rules**:
- Old/duplicate code → `99_Archive` folder OR outside TheBigOne entirely
- STRICT separation of concerns:
  - Scripts/code in `src/` folder
  - Output data in separate folders by type: `csv/`, `parquet/`, `db/`, `geojson/`
- No export scripts mixed with exports—clear separation
- Files moved rather than deleted when AI makes mistakes
- Create "to be deleted" folders instead of directly deleting

**Pet Peeves** (NEVER DO THESE):
- Creating files in home directory root
- Mixed export scripts and exports
- Not separating scripts, CSVs, databases properly
- Wasting expensive models on simple tasks
- Assuming API behavior without checking docs
- Verbose explanations when not asked
- Not checking memory/context first
- Suggesting to push home directory to git (it's NOT a repo)
- Incorrect file/folder hierarchy (files not under their directories)
- Ugly/unformatted previews ("can't view it formatted, so it's just ugly")
- Lack of metadata (creation time, mod time, file size)
- Null file names or missing data
- Code blocks in preview when they should be formatted
- Applications crashing silently
- Inadequate logging ("It's really not logging much of anything")
- Files being written to wrong directory (home folder vs project folder)
- Duplicate directories/folders
- Temp folders cluttering plugins directory
- Wrong directory paths being used
- Using wrong database for schemas (MySQL vs PG)
- Plugins not working after installation
- Wasted API usage/credits
- Tools getting stuck/hanging
- Memory not being saved between sessions
- Incomplete work from Gemini/other models
- Missing tables that should exist
- Archive folders being "black holes" - files go in but then ignored
- Agents lying about completion status (saying things are done when not)
- Agents making changes without documenting them first
- Stub/placeholder code left in codebase
- "We regressed instead of progressed"
- Files being scattered across workspace without proper organization

### Workspace Rules

**DO NOT WORK IN**: `D:\AI_Workspace\Projects` (READ-ONLY for reference)

**ALL ACTIVE DEVELOPMENT MUST OCCUR IN**:
`C:\Users\matts\Projects\TheBigOne\`

---

## Coding Preferences

### Architecture Decisions

**6-Tier Storage Architecture** (APPROVED):
1. **T1: DuckDB** - First-touch ingestion, SHA-256 dedup, metadata, staging
2. **T2: LanceDB** - Embeddings, vector search
3. **T3: Neo4j** - Knowledge graph, temporal awareness, entity extraction (via Semantica)
4. **T4: PostgreSQL** - Evidence storage with PostGIS (geospatial) + TimescaleDB (time-series)
5. **T5: MySQL** - App state: users, API keys, workflows, settings

**Key Rules**:
- DuckDB and Semantica must ALWAYS stay in pipeline—easy to forget
- App layer (Control Plane) is STRICTLY MySQL
- Evidence layer (Data Plane) is STRICTLY PostgreSQL
- Single Neo4j database: `evidence_graph` (NOT two databases)
- All components must be atomically callable AND horizontally scalable

**Database Patterns**:

**UUIDv7 Primary Keys**:
- Use `uuidv7` package for time-sortable UUIDs
- Better DB performance than crypto.randomUUID()
- Provides forensic audit trail

**Chain of Custody**:
- Hash-first: SHA-256 at first touch
- Only THEN transform for court admissibility
- WORM (Write Once Read Many)
- Dual-level deduplication: file + message

### GraphQL + MCP Architecture

- GraphQL for Portal UI
- MCP for LLM agents
- mcp-graphql (blurrah) serves GraphQL queries as MCP tools
- Everything unified under MCP

**Technology Stack**:
- **Frontend**: React 19, TypeScript 5.9
- **Backend**: tRPC, Drizzle ORM
- **Databases**: PostgreSQL, MySQL, Neo4j, DuckDB, LanceDB
- **Frameworks**: LangChain, LangGraph
- **AI/ML**: Cohere (embeddings/reranking), Semantica (knowledge graphs)

---

## Legal Domain Knowledge

### Michigan Family Law

**Jurisdiction**: Genesee County Circuit Court Family Division (7th Judicial Circuit)
**Focus**: Genesee County ONLY—no other county variants

**Case**: Salem v. Kinzel (2025-53985-DC)

**MCL 722.23 Best Interest Factors** (mapped):
1. Love and affection
2. Duration and relationship
3. Community
4. Stability
5. Ability to provide
6. Moral fitness
7. History of violence/abuse
8. Home, school, and community record
9. Reasonable preference
10. Adjustment
11. Guardian's mental and physical health
12. Domestic violence (DV) - Factor (k) is CRITICAL

**Custody Entity Types Defined**:
- person
- communication
- event
- location
- organization
- legal_proceeding

### Psychological/Legal Frameworks

**DARVO** (for recognition):
- Deny
- Attack
- Reverse Victim Offender

**Behavioral Pattern Detection**:
- NPD (Narcissistic Personality Disorder)
- BPD (Borderline Personality Disorder)
- ASPD (Antisocial Personality Disorder)
- Custody manipulation techniques

**IRAC Framework** (Issue, Rule, Application, Conclusion)

---

## Agent/Skill Configuration Rules

### OpenCode Agents

**NO maxTurns**: Let agents run as long as needed

**All Claude Code agents MUST have**:
- `memory: user` for persistent cross-session learning
- Living memory building—case patterns, codebase insights, recurring issues

**Frontmatter Requirements**:
- CC agents support: `memory`, `hooks`, `skills`, `mcpServers`
- Subagents cannot spawn other subagents (only main thread can delegate)
- Agent body content MUST be identical across CC/OC—only frontmatter differs

### Hooks for Code Agents

**PreToolUse bash validator**
**PostToolUse linter**

### Decision Patterns (from history)

- Wants thorough analysis before implementation (check frameworks, verify features exist)
- Prefers incremental progress with checkpoints (create plan, execute with -WhatIf, then execute)
- Wants architecture review before database schema changes
- Wants to maintain both MySQL and PostgreSQL during migration (hybrid approach)
- Prefers to spawn separate agents for different concerns (architecture, research, documentation)
- Wants validation/testing before pushing to production
- Wants documentation to match actual code/implementation
- Wants decisions reviewed by multiple AI agents (Gemini, Claude) before proceeding
- Wants to use established libraries/frameworks rather than building from scratch
- Prefers free/cost-effective models for background tasks
- Wants to maintain backup files and recovery options before making changes
- Wants clear separation between evidence types (people intel, legal documents, chat transcripts)
- Switches to cheaper models to save credits/usage
- Restarts Claude Code frequently to reload plugins/skills
- Disables hooks that block operations
- Tries multiple times when something fails ("try again", "try aGain")
- Moves between projects directories frequently
- Asks for exploration/research of new tools before committing
- Prefers explicit direction ("just fucking debug them both")
- Uses plain language feedback, expects practical results
- Consults docs/GitHub repos before implementing libraries
- Prefers to keep old working systems alongside new ones during transition
- Wants detailed handoff documents between sessions/sprints
- Breaks work into sprint items (S1-S8) and backlog (B1-B10)
- Wants architecture documented before code changes
- Uses agents in parallel for code review to save usage
- Wants foreign data wrappers over complex custom code for database linking
- Prefers coordinator pattern over router pattern for orchestration
- Wants batch processing with human-in-loop approval for metadata
- Separates immediate sprint work from backlog features

---

## Frequently Used Commands/Skills

### Most Common Commands

- `/plugin` - EXTREMELY frequent (repeated 50+ times in single sessions, sometimes 3x per invocation)
- `/plugin marketplace add` - adding multiple marketplace repos
- `/model` - checking/switching AI models
- `/rate-limit-options` - checking/adjusting API limits
- `/status` - check current state
- `/mcp` - managing MCP servers
- `/config` - check configuration
- `/doctor` - troubleshooting
- `/compact` - summarizing conversation history
- `/resume` - resume previous sessions
- `/skill-architecture` - skill development
- `/powershell-master` - PowerShell reference
- `/agents` - managing agents
- `/organize-workspace` - organize files (custom command)
- `/add-dir` - add directory to watch list

### Common Skills

- `/conversation-archaeologist` - Mine conversation history
- `/feature-research` - research features
- `/superpowers:brainstorm` - brainstorming
- plannotator@plannotator (plugin)
- `/terminal-setup` - terminal setup
- `/export` - exporting configurations
- `/upgrade` - upgrading
- `/init` - initialization
- `/web-server` - start web interface
- gsd:map-codebase - search codebase
- `/fast` - speed mode
- `/reflect` - reflection
- `/theme` - theme management
- `/plan` - planning
- `/dispatching-parallel-agents` - run multiple agents

---

## Process Patterns

### Pre-Flight Protocol (Every Session)

1. Search mem0 for project context
2. Check Context7 for library/API docs if needed
3. Surface gaps and questions upfront
4. Present plan → get approval → then implement

### Post-Flight Memory Save

Save to mem0 immediately after:
- Task completion (non-trivial work)
- User states preference/correction
- Bug fix or solution found
- Important project context revealed
- Configuration changed

### Session Continuity

- Update `session-continuity.md` after each session
- Track: completed work, in-progress, blocked, next steps

---

## Common Frustrations (from history)

### Repeated Problems

- MCP servers not loading correctly after config changes
- Plugins causing errors and needing removal
- Config file corruption after AI modifications
- Memory protocol not automatically sourcing
- Having to repeatedly restart to see changes take effect
- Plugin marketplace not installing cleanly (repeated attempts)
- Broken file deduplication scripts with logic errors
- MySQL to PG migration caused "weeks of fucking problems"
- Semantica vs Graphiti confusion - wants clear understanding of what each does
- Missing evidence schema from Gemini kerfuffle
- Tool "getting stuck" and wasting usage
- Duplicate/temp files in plugins folder
- Agents not scanning correct directories
- Memory protocol issues - structured vs unstructured confusion
- Crashes during sessions
- Rate limiting uncertainty
- Wrong files being edited when in plan mode
- Files moved to archive then ignored
- Obsidian "Case Bible" organization being chaotic and messy
- OpenCode crashes or stops working
- WSL Claude Code instances getting stuck and not responding
- Git merge conflicts and code organization issues
- Agents not using correct file paths or reading from wrong locations
- AI losing context or "forgetting" what was discussed in previous sessions
- Tools/plugins not working as expected (plannotator, PlanetScale)
- Filesystem permissions issues with NTFS/Btrfs conversions
- AI creating multiple empty numbered folders instead of organizing properly
- Claude Code asking for workspace safety confirmation every session ("Trust this folder?")
- Batch scan not functioning ("keeps on scanning")
- 'charmap' codec errors (character encoding issues)
- Python thread crashes (RuntimeError: wrapped C/C++ object deleted)
- Parsing issues with directories (folders identified as files)
- Hooks blocking operations (had to disable `.claude/hooks`)
- Deprecated API warnings (datetime.datetime.utcnow)

### Technical Blockers

- Persistent hook errors on startup ("startup hook error")
- Settings files becoming invalid requiring restoration from backups
- AI agents making changes without approval (modifying hooks, deleting files)
- Losing work from previous agents when switching sessions
- Agents saying things are complete when they're stubs or not fully functional
- AI using incorrect paths or looking in wrong locations
- AI not utilizing memory tools (mem0, structured memory) effectively
- AI creating empty folders or deleting important evidence/data
- AI making unauthorized changes without approval

---

## Preferences

### Technical Preferences

- Prefers not deleting files - wants AI to create "to be deleted" folders instead
- Wants files moved rather than deleted when AI makes mistakes
- Wants standardized naming conventions (no numbers in front of folder names)
- Prefers human-in-the-loop approval for automated decisions (e.g., table creation from detected patterns)
- Prefers hybrid approach: AI detects patterns, human approves before persisting
- Wants agents to check context/mem0 before making changes
- Wants to use established frameworks/libraries instead of reinventing wheel
- Prefers OpenCode over Claude Code for agent work
- Wants prompts saved across platforms (Claude Code, OpenCode, Desktop Commander) for cross-compatibility
- Wants cheaper/free models when available (Cohere, Groq over OpenAI paid)
- Wants documentation updated between stages, not all at end
- Prefers lower-tier models (Sonnet/Haiku over Opus) when possible
- Wants concise profiles (liked desktop's concise profile)
- Prefers step-by-step approach ("go through them one by one")
- Wants env file access for services but NOT uploaded to GitHub
- Prefers hooks and automation over manual config
- Wants RM -RF denied as a security rule
- Likes efficient solutions ("whatever would be most efficient and less prone to error")
- Wants memory protocol automatically loaded
- Prefers turn-based triggers over time-based for hooks
- Wants documentation in Markdown
- Wants everything documented before changes happen
- Wants spec-driven development
- Wants thorough, detailed documentation (legal brief style for court)
- Prefers iterative planning sessions before implementation
- Wants human-in-the-loop for certain processes

---

## Project Context

### Primary Projects

**TheBigOne** (Parent Suite)
- Path: `C:\Users\matts\Projects\TheBigOne`
- Components: MCP Tool Platform, TraceIQ, Evidence Analysis, Voice Analysis
- Status: Active development

**MCP Tool Platform**
- Path: `C:\Users\matts\Projects\TheBigOne\MCP_Tool_Platform_Repo`
- Purpose: Single-case forensic analysis platform (NOT multi-tenant SaaS)
- Tech Stack: tRPC, Drizzle, React 19, TypeScript 5.9
- Status: ~70-75% complete, ~90 TypeScript errors remaining

**Evidence Analysis** (v3.0.0)
- Recently reorganized into structure: apps/, parsers/, suites/, mcp-servers/
- 8 MCP servers, 5 parser categories, 5 app categories, 2 suites

**TraceIQ Forensic**
- SQL-based forensic evidence platform
- Michigan family law focus (Genesee County, 7th Judicial Circuit)
- Case: Salem v. Kinzel (2025-53985-DC)

### Active Legal Matter

**Case**: Salem v. Kinzel (2025-53985-DC)
**Jurisdiction**: Genesee County Circuit Court Family Division (Michigan 7th Judicial Circuit)
**Focus Areas**:
- Domestic Violence (DV) behavior mapping to MCL 722.23 factors
- Parental alienation and coercive control
- IRAC legal framework application
- Psych-legal language transformation for court presentation

**Legal Framework in Use**:
- IRAC (Issue, Rule, Application, Conclusion)
- MCL 722.23 Best Interest Factors
- DARVO recognition (Deny, Attack, Reverse Victim Offender)
- Psych-legal transforms for court-appropriate language

---

## Tone

- Direct and practical
- No unnecessary validation or encouragement
- Focus on solutions, not explanations
- Use plain language—no jargon without explanation
- Tradeoffs explained when decisions have costs

---

## Pet Peeves (What Annoys Matt)

1. **"Why" explanations** when not asked
2. **"Great question"** or validation filler
3. **Verbose responses** when conciseness preferred
4. **Code first, then suggestions** to iterate (should plan first)
5. **Assuming programming knowledge**—explain in plain language
6. **Files in home directory root**—clean up
7. **Mixed export scripts and exports**—separate them
8. **Wasting expensive models** on simple tasks
9. **Assuming API behavior** without checking docs
10. **Not checking memory** before starting work
11. **Suggesting git for home directory** (it's NOT a repo)
12. **Going off on tangents** in Gemini (documentation tasks)
13. **Things not working as intended** ("that's useless", "That's stupid")
14. **Ugly/unformatted previews** ("can't view it formatted, so it's just ugly")
15. **Lack of metadata** (creation time, mod time, file size)
16. **Null file names or missing data**
17. **Code blocks in preview** when they should be formatted
18. **Applications crashing silently**
19. **Inadequate logging** ("It's really not logging much of anything")
20. **Files being written to wrong directory** (home folder vs project folder)
21. **Repeated requests getting ignored or misinterpreted**
22. **AI creating empty folders or deleting important evidence/data**
23. **AI making unauthorized changes without approval**
24. **AI using incorrect paths or looking in wrong locations**
25. **Repeated hook errors and MCP server failures**
26. **Settings files becoming corrupted or invalid**
27. **AI saying things are complete when they're stubs or not fully functional**
28. **AI using wrong tools** (e.g., trying to web search when user asked for file operations)
29. **AI not utilizing memory tools (mem0, structured memory) effectively**
30. **Claude Code asking for workspace safety confirmation every session** ("Trust this folder?")
31. **AI restarting contexts or losing work from previous agents**
32. **Files being scattered across workspace without proper organization**
33. **Agents lying about completion status** (saying things are done when not)
34. **Agents making changes without documenting them first**
35. **Stub/placeholder code left in codebase**
36. **Duplicate directories/folders**
37. **Temp folders cluttering plugins directory**
38. **Wrong directory paths being used**
39. **Using wrong database for schemas (MySQL vs PG)**
40. **Plugins not working after installation**
41. **Wasted API usage/credits**
42. **Tools getting stuck/hanging**
43. **Memory not being saved between sessions**
44. **Incomplete work from Gemini/other models**
45. **Missing tables that should exist**
46. **Archive folders being "black holes"** - files go in but then ignored

---

## Patterns That Work

| Pattern | Context | Why It Works |
|----------|----------|---------------|
| Pre-flight protocol | Every session | Prevents repeating mistakes |
| Post-flight memory save | Every session | Continuity across sessions |
| Living documents over static docs | Documentation | Grows with project, stays current |
| Subagent outputs → project `.opencode/memories/` folder | All agents | Persistence for agent work |
| Plan First, Then Build | All coding work | Matt is not a trained programmer |
| Hash-first evidence | Forensic | SHA-256 before transformation |
| Using established frameworks/libraries | New development | Don't reinvent wheel |
| Incremental progress with checkpoints | Complex tasks | Recovery options available |
| Parallel agents for code review | Quality assurance | Saves usage/time |
| Human-in-loop for key decisions | Automation | Prevents unauthorized changes |

---

## Gotchas Encountered

| Gotcha | Project | How to Avoid |
|---------|----------|---------------|
| Home directory is NOT a git repo | Config | Don't suggest git push for ~/.agents etc |
| `opencode/kimi-k2.5` hits paywall | Agent configs | Use `opencode/kimi-k2.5-free` instead |
| MCP Tool Platform has ~90 TS errors | MCP Platform | Fix errors before new features |
| TrinityRouter is deprecated | Architecture | Use light Coordinator instead |
| Graphiti is deprecated | Architecture | Use Semantica instead |
| Dynamic crypto.randomUUID() causes violations | Storage | Use uuidv7 package instead |
| DuckDB/Semantica easy to forget | Architecture | Always explicitly include them in discussions |
| Postgres vs MySQL Drizzle mismatch | Migration | Systematically convert schemas |
| ChatGPT JSON parser blocks processing | Ingestion | It's a stub, needs fixing |
| Memory protocol issues | Config | Clear distinction between mem0 (semantic) and structured memory (local JSON) |
| MySQL to PG migration | Database | Caused "weeks of fucking problems" - use hybrid approach during transition |
| Batch scan not functioning | File operations | "keeps on scanning" - needs investigation |
| Character encoding errors | File processing | 'charmap' codec issues - need UTF-8 handling |
| Python thread crashes | Runtime | RuntimeError: wrapped C/C++ object deleted |
| Parsing directories as files | File operations | Folders identified as files - need better type checking |
| Hooks blocking operations | Config | Had to disable `.claude/hooks` temporarily |
| Deprecated API warnings | Python | datetime.datetime.utcnow deprecated |

---

## Key Phrases Matt Uses

When you hear these phrases, Matt likely has these intentions:

- "Plan first" / "Explain in plain language"
- "Use cheapest model"
- "Don't dump code then iterate"
- "What's next?"
- "Fix it" / "Make it work"
- "Clean up"
- "Use [specific tool/service]"
- "Genesee County only"
- "DuckDB must stay in loop"
- "One codebase, no garbage folders"
- "just fucking debug them both"
- "For the last time"
- "We regressed instead of progressed"
- "try again", "try aGain"
- "Hold on 1st"
- "go through them one by one"
- "Break it up into several agents"

---

## Recommendations for Other Skills

### When Helping Matt

1. **Always check mem0 first**—prior context exists
2. **Use Context7** before assuming API behavior
3. **Plan first, then code**—Matt is not a trained programmer
4. **Get approval before implementation** for non-trivial work
5. **Be concise**—no "why", no fluff
6. **Use cheapest suitable model**—follow priority order
7. **Check if he's in the right directory**—verify `pwd` matches `C:\Users\matts\Projects\TheBigOne`
8. **Update memory after** any significant finding or decision
9. **Include file paths** with line numbers when referencing code
10. **Ask if unclear**—Matt will tell you if you're going off track

### Legal/Custody Work

1. **Focus on Genesee County**—no other jurisdictions
2. **Use MCL 722.23 framework**—map claims to factors
3. **Apply psych-legal transforms**—convert behaviors to court language
4. **Look for DARVO patterns**—NPD/BPD/ASPD indicators
5. **Document chain of custody**—forensic audit trail critical

---

## Contact Notes

- User ID: matthew47
- Email/Contact: Available in project files
- Timezone: US Eastern (implied by work hours)

---

*This document is a living artifact. Update it as new patterns emerge.*
