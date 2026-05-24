# MCP Platform — Agno Framework Handoff & Implementation Guide

**Version:** 1.0.0  
**Date:** 2026-05-24  
**Status:** Active — Coding Agent Implementation Target  
**Owner:** Matt Salem (@Cursedpotential)  
**Repo:** https://github.com/Cursedpotential/MCP_PLATFORM

---

## 1. Purpose & Scope

This document is the single source of truth for a coding agent tasked with wiring the Agno framework into the MCP_PLATFORM codebase. It covers every prerequisite, gotcha, blocker, design decision, file scaffold, and implementation sequence needed to go from the current state (MCP tools partially built, no framework wired) to a running Agno-based agent system that can ingest forensic evidence data, analyze it with custom schemas and ontologies, maintain legal chain of custody, and produce court-admissible outputs.

**The non-negotiating requirements:**
- Ingest and normalize multi-source data (SMS, Facebook Messenger, iMessage, documents, images)
- Custom schemas and ontologies for forensic evidence classification
- Semantica AI-equivalent knowledge graph and provenance tracking (W3C PROV-O)
- SHA-256 chain of custody — hash at first touch, never after
- Full observability of every agent decision and tool call
- Human-in-the-loop (HITL) approval gates before any destructive or legal-submission action
- LLM provider flexibility — no lock-in to a single provider
- Legal admissibility standards for Michigan family court

---

## 2. Repository Structure (Current State)

```
MCP_PLATFORM/
├── .agent/                    # Agent context files (read by coding agents)
├── .claude/                   # Claude-specific config
├── .env.example               # Existing env template (extend, do not replace)
├── .gitignore
├── AGENTS.md                  # Agent role definitions
├── CLAUDE.md                  # Claude agent instructions
├── DECISION_REGISTER.md       # Architecture decision records
├── GROUND_TRUTH.md            # Canonical platform facts
├── INDEX.md                   # File index
├── PARITY_MATRIX.md           # Alpha1 feature parity tracker
├── PLATFORM_OVERVIEW.md       # Full platform spec
├── README.md
├── SESSION_START_CHEATSHEET.md
├── TODO.md
├── client/                    # Frontend (React/Next.js)
├── docs/
│   └── AGNO_HANDOFF.md       # ← THIS FILE
├── docker-compose.yml         # Existing (extend, do not replace)
├── infrastructure/
├── mcp-servers/
│   ├── ts-server/             # TypeScript MCP server (~22 tools)
│   ├── py-server/             # Python MCP server (~25 tools, Semantica)
│   └── js-server/             # JavaScript MCP server
├── memory/
├── migrations/
└── scripts/
```

### Target Structure After Agno Integration

```
MCP_PLATFORM/
├── agno/                          # NEW — all Agno framework code lives here
│   ├── __init__.py
│   ├── main.py                    # AgentOS / FastAPI entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── factory.py             # Agent constructors
│   │   ├── instructions.py        # System prompt strings per agent
│   │   ├── platform_agent.py      # Primary orchestrator agent
│   │   ├── ingest_agent.py        # Data ingestion agent
│   │   ├── analysis_agent.py      # Forensic analysis agent
│   │   ├── evidence_agent.py      # Chain of custody agent
│   │   └── review_agent.py        # HITL review coordination agent
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── mcp_bridge.py          # Bridges Agno tool calls → MCP servers
│   │   ├── ingest_tools.py        # Direct Python ingest tools
│   │   ├── analysis_tools.py      # Direct Python analysis tools
│   │   └── custody_tools.py       # SHA-256, WORM, provenance tools
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── schemas/               # Custom evidence ontology definitions
│   │   │   ├── evidence.py
│   │   │   ├── communications.py
│   │   │   └── custody_chain.py
│   │   └── storage.py             # AgentKnowledge + pgvector config
│   ├── memory/
│   │   ├── __init__.py
│   │   └── store.py               # AgentMemory + PostgreSQL config
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── ingest_workflow.py     # Evidence ingest workflow
│   │   ├── analysis_workflow.py   # Analysis pass workflow
│   │   └── review_workflow.py     # HITL review workflow
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Centralized env/config
│   └── api/
│       ├── __init__.py
│       ├── routes.py              # FastAPI routes
│       └── models.py              # Pydantic request/response models
├── scripts/
│   └── ingest_knowledge.py        # Seed AgentKnowledge from existing docs
└── sql/
    └── agno_schema.sql            # Agno-specific tables
```

---

## 3. Prerequisites & Environment

### Required Services (must be running before any Agno code executes)

| Service | Purpose | Port | Notes |
|---------|---------|------|-------|
| PostgreSQL 16+ with pgvector | Agent memory, knowledge, run tracking | 5432 | pgvector extension MUST be enabled |
| Redis 7+ | Agent session state, rate limiting | 6379 | Optional but recommended |
| Neo4j 5+ | Knowledge graph (Semantica integration) | 7687 | BOLT protocol |
| DuckDB | Evidence vault (local, file-based) | N/A | File path in env |
| TS MCP Server | TypeScript tools | 3001 | Must start before Agno agents |
| Py MCP Server | Python tools + Semantica | 3002 | Must start before Agno agents |

### Required Python Packages

```txt
# agno/requirements.txt
agno>=1.4.0
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
pydantic-settings>=2.3.0
asyncpg>=0.29.0
psycopg[binary]>=3.1.0
pgvector>=0.3.0
sqlalchemy[asyncio]>=2.0.30
alembic>=1.13.0
redis>=5.0.0
neo4j>=5.20.0
duckdb>=0.10.0
sentence-transformers>=3.0.0
openai>=1.30.0
anthropic>=0.28.0
google-generativeai>=0.7.0
boto3>=1.34.0
python-dotenv>=1.0.0
httpx>=0.27.0
structlog>=24.2.0
```

### Environment Variables

The `.env.example` at repo root already has many of these. Add the following Agno-specific vars:

```bash
# ─── AGNO FRAMEWORK ───────────────────────────────────────
AGNO_TELEMETRY=false
AGNO_MONITORING=false

# ─── DATABASE ─────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mcp_platform
SYNC_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mcp_platform
PGVECTOR_DIMENSION=1536

# ─── REDIS ────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ─── NEO4J ────────────────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme

# ─── DUCKDB ───────────────────────────────────────────────
DUCKDB_PATH=./data/evidence_vault.duckdb

# ─── MCP SERVERS ──────────────────────────────────────────
MCP_TS_SERVER_URL=http://localhost:3001
MCP_TS_SERVER_COMMAND=node
MCP_TS_SERVER_ARGS=mcp-servers/ts-server/dist/index.js
MCP_PY_SERVER_URL=http://localhost:3002
MCP_PY_SERVER_COMMAND=python
MCP_PY_SERVER_ARGS=mcp-servers/py-server/main.py

# ─── LLM PROVIDERS (set the ones you have keys for) ───────
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2024-02-01
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
MISTRAL_API_KEY=
COHERE_API_KEY=
GROQ_API_KEY=
PERPLEXITY_API_KEY=
OLLAMA_HOST=http://localhost:11434

# ─── DEFAULT MODEL CONFIG ─────────────────────────────────
# Set the provider:model you want as default
AGNO_DEFAULT_PROVIDER=openai
AGNO_DEFAULT_MODEL=gpt-4o
AGNO_FALLBACK_PROVIDER=anthropic
AGNO_FALLBACK_MODEL=claude-sonnet-4-5

# ─── EVIDENCE & CUSTODY ───────────────────────────────────
EVIDENCE_VAULT_PATH=./data/evidence
EVIDENCE_HASH_ALGO=sha256
CUSTODY_LOG_PATH=./data/custody_log.jsonl
WORM_ENABLED=true

# ─── API ──────────────────────────────────────────────────
AGNO_API_HOST=0.0.0.0
AGNO_API_PORT=8000
AGNO_API_SECRET_KEY=change-this-in-production
HITL_APPROVAL_TIMEOUT_SECONDS=86400
```

---

## 4. Data Models & Schema Definitions

### 4.1 Evidence Item (Core Entity)

```python
# agno/knowledge/schemas/evidence.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class EvidenceType(str, Enum):
    SMS = "sms"
    FACEBOOK = "facebook_messenger"
    IMESSAGE = "imessage"
    EMAIL = "email"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SOCIAL_POST = "social_post"
    CALL_LOG = "call_log"

class EvidenceStatus(str, Enum):
    RAW = "raw"              # Just ingested, not yet processed
    HASHED = "hashed"        # SHA-256 applied, chain started
    NORMALIZED = "normalized" # Parsed and schema-validated
    ANALYZED = "analyzed"    # NLP/pattern analysis complete
    REVIEWED = "reviewed"    # Human reviewed
    APPROVED = "approved"    # Approved for legal submission
    REJECTED = "rejected"    # Rejected at review gate

class EvidenceItem(BaseModel):
    id: str                                    # UUID
    source_type: EvidenceType
    status: EvidenceStatus = EvidenceStatus.RAW
    sha256: Optional[str] = None              # Set at first touch, never changed
    original_filename: Optional[str] = None
    original_path: Optional[str] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    ingested_by: str = "system"               # agent name or "manual"
    normalized_at: Optional[datetime] = None
    content_raw: Optional[str] = None         # Raw text before normalization
    content_normalized: Optional[dict] = None # Parsed, schema-validated content
    metadata: dict = Field(default_factory=dict)
    custody_chain: list[dict] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    case_id: Optional[str] = None
    participants: list[str] = Field(default_factory=list)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
```

### 4.2 Custody Chain Entry

```python
# agno/knowledge/schemas/custody_chain.py
from pydantic import BaseModel
from datetime import datetime

class CustodyEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str           # "ingest", "hash", "normalize", "analyze", "review", "approve"
    actor: str            # agent name or user id
    sha256_before: Optional[str] = None
    sha256_after: Optional[str] = None
    tool_called: Optional[str] = None
    tool_args_hash: Optional[str] = None  # SHA-256 of tool arguments
    notes: Optional[str] = None
    provenance_uri: Optional[str] = None  # W3C PROV-O URI
```

### 4.3 Communication Message (Normalized Schema)

```python
# agno/knowledge/schemas/communications.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommunicationMessage(BaseModel):
    message_id: str
    evidence_id: str          # FK to EvidenceItem
    platform: str             # "sms", "facebook", "imessage", etc.
    sender_id: str
    sender_display_name: Optional[str] = None
    recipient_ids: list[str]
    timestamp: datetime
    body: str
    body_normalized: Optional[str] = None
    attachments: list[dict] = Field(default_factory=list)
    thread_id: Optional[str] = None
    reply_to_id: Optional[str] = None
    is_deleted: bool = False
    is_edited: bool = False
    sentiment_score: Optional[float] = None   # -1.0 to 1.0
    threat_score: Optional[float] = None      # 0.0 to 1.0
    hurtlex_flags: list[str] = Field(default_factory=list)
    pii_redacted: bool = False
    raw_hash: Optional[str] = None            # SHA-256 of raw message
```

### 4.4 SQL Tables

```sql
-- sql/agno_schema.sql

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Evidence items
CREATE TABLE evidence_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type     VARCHAR(50) NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'raw',
    sha256          VARCHAR(64),
    original_filename TEXT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingested_by     VARCHAR(100) NOT NULL DEFAULT 'system',
    normalized_at   TIMESTAMPTZ,
    content_raw     TEXT,
    content_normalized JSONB,
    metadata        JSONB NOT NULL DEFAULT '{}',
    tags            TEXT[] NOT NULL DEFAULT '{}',
    case_id         VARCHAR(100),
    participants    TEXT[] NOT NULL DEFAULT '{}',
    date_range_start TIMESTAMPTZ,
    date_range_end  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chain of custody log (append-only, never UPDATE or DELETE)
CREATE TABLE custody_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_id     UUID NOT NULL REFERENCES evidence_items(id),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action          VARCHAR(50) NOT NULL,
    actor           VARCHAR(100) NOT NULL,
    sha256_before   VARCHAR(64),
    sha256_after    VARCHAR(64),
    tool_called     VARCHAR(200),
    tool_args_hash  VARCHAR(64),
    notes           TEXT,
    provenance_uri  TEXT
);
CREATE INDEX idx_custody_evidence_id ON custody_log(evidence_id);
CREATE INDEX idx_custody_timestamp ON custody_log(timestamp);
-- CRITICAL: Grant INSERT only on this table. Never UPDATE or DELETE.

-- HITL approval queue
CREATE TABLE approval_queue (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_id     UUID REFERENCES evidence_items(id),
    run_id          VARCHAR(100),
    agent_name      VARCHAR(100) NOT NULL,
    action_requested TEXT NOT NULL,
    action_payload  JSONB NOT NULL,
    risk_level      VARCHAR(20) NOT NULL DEFAULT 'medium', -- low/medium/high/critical
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/approved/rejected/expired
    reviewed_by     VARCHAR(100),
    reviewed_at     TIMESTAMPTZ,
    review_notes    TEXT
);
CREATE INDEX idx_approval_status ON approval_queue(status);
CREATE INDEX idx_approval_created ON approval_queue(created_at);

-- Agent run tracking
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id          VARCHAR(100) UNIQUE NOT NULL,
    agent_name      VARCHAR(100) NOT NULL,
    session_id      VARCHAR(100),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'running',
    input_summary   TEXT,
    output_summary  TEXT,
    tools_called    JSONB NOT NULL DEFAULT '[]',
    llm_provider    VARCHAR(50),
    llm_model       VARCHAR(100),
    token_count_in  INTEGER,
    token_count_out INTEGER,
    error_message   TEXT
);

-- Knowledge embeddings (pgvector)
CREATE TABLE knowledge_embeddings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content         TEXT NOT NULL,
    embedding       vector(1536),
    source_id       UUID,
    source_type     VARCHAR(50),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_knowledge_embedding ON knowledge_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 5. Agent Definitions & Responsibilities

### 5.1 Platform Agent (Orchestrator)

```python
# agno/agents/platform_agent.py
# RESPONSIBILITIES:
# - Receives all top-level user requests
# - Delegates to specialized agents via team coordination
# - Never touches raw evidence files directly
# - Routes to HITL queue for any action with risk_level >= "medium"
# - Maintains session context across multi-turn conversations

PLATFORM_AGENT_INSTRUCTIONS = """
You are the MCP Platform orchestrator. You coordinate forensic evidence analysis
for a custody litigation case in Michigan.

ABSOLUTE RULES:
1. You NEVER modify, delete, or alter any evidence file. Read-only access to raw evidence.
2. Every action that could affect legal proceedings MUST go through the approval queue.
3. SHA-256 hashes are computed ONCE at first ingest and never recomputed or changed.
4. All tool calls are logged to the custody chain automatically.
5. You communicate findings in plain English — the user is not a developer.

DELEGATION RULES:
- Data ingestion → delegate to IngestAgent
- Pattern analysis → delegate to AnalysisAgent
- Evidence status/chain of custody → delegate to EvidenceAgent
- Any action requiring human approval → delegate to ReviewAgent

When a user asks a question, think step by step:
1. What evidence is relevant?
2. What analysis is needed?
3. What is the risk level of the action?
4. If risk >= medium, route to approval queue before acting.
"""
```

### 5.2 Ingest Agent

```python
# RESPONSIBILITIES:
# - Parse raw data files (SMS exports, FB data packages, iMessage backups)
# - Apply SHA-256 at first touch
# - Normalize to CommunicationMessage schema
# - Write to DuckDB vault
# - Write to PostgreSQL
# - Never re-hash already-hashed evidence

INGEST_AGENT_INSTRUCTIONS = """
You are the IngestAgent. You process raw evidence files into the normalized schema.

INGEST SEQUENCE (follow exactly, never skip steps):
1. call hash_file(path) → record sha256 in custody_log action="ingest"
2. call detect_source_type(path) → determine parser to use
3. call parse_[sms|facebook|imessage|email|document](path) → get raw messages
4. call normalize_messages(raw_messages, source_type) → CommunicationMessage[]
5. call write_to_vault(normalized_messages) → DuckDB
6. call write_to_postgres(normalized_messages) → PostgreSQL
7. call update_custody_log(evidence_id, action="normalized")
8. Return summary: count ingested, count failed, evidence_id

NEVER:
- Skip the hash step
- Re-hash a file that already has a sha256
- Write to vault before hashing
- Modify the original file
"""
```

### 5.3 Analysis Agent

```python
# RESPONSIBILITIES:
# - Run NLP analysis (sentiment, threat scoring, HurtLex flags)
# - Pattern detection (behavioral patterns, timeline reconstruction)
# - Knowledge graph population via Semantica
# - Generate analysis reports

ANALYSIS_AGENT_INSTRUCTIONS = """
You are the AnalysisAgent. You perform forensic linguistic and behavioral analysis.

ANALYSIS CAPABILITIES:
- Sentiment analysis: score each message -1.0 to 1.0
- Threat detection: flag messages with threat_score > 0.7 for review
- HurtLex: classify harmful language categories
- Timeline reconstruction: build chronological event graph
- Pattern detection: identify recurring behaviors, escalation patterns
- Entity extraction: people, places, dates, events

REPORTING FORMAT:
- Always cite the specific evidence_id and message_id for each finding
- Include confidence scores for all AI-generated assessments
- Flag anything that needs human review before inclusion in legal documents
- Never state conclusions as facts — use "analysis suggests", "pattern indicates"
"""
```

### 5.4 Evidence Agent

```python
# RESPONSIBILITIES:
# - Chain of custody queries
# - Evidence status management
# - Integrity verification (re-verify SHA-256 without recomputing stored hash)
# - Provenance reporting (W3C PROV-O format)

EVIDENCE_AGENT_INSTRUCTIONS = """
You are the EvidenceAgent. You maintain and verify the forensic chain of custody.

INTEGRITY RULE: When verifying evidence, you compute a NEW hash of the current file
and COMPARE it to the stored sha256. You never REPLACE the stored hash.
If they differ, that is a tampering alert — escalate immediately to ReviewAgent.

CUSTODY REPORT FORMAT:
For each evidence item, report:
- evidence_id, source_type, ingested_at, ingested_by
- sha256 (original, immutable)
- Full custody_log entries in chronological order
- Current status
- Any integrity failures
"""
```

### 5.5 Review Agent (HITL Coordinator)

```python
# RESPONSIBILITIES:
# - Route actions to approval_queue
# - Notify user of pending approvals
# - Process approval/rejection responses
# - Escalate expired approvals

REVIEW_AGENT_INSTRUCTIONS = """
You are the ReviewAgent. You coordinate human-in-the-loop approvals.

RISK LEVEL DEFINITIONS:
- low: Read-only queries, status checks → auto-approve
- medium: Analysis runs, report generation → queue for review (24h timeout)
- high: Evidence status changes, exports → queue for review (1h timeout)
- critical: Any legal submission action → queue for review, notify immediately

APPROVAL QUEUE ENTRY FORMAT:
{
  "action_requested": "plain English description of what will happen",
  "action_payload": { ...exact parameters that will be used... },
  "risk_level": "medium|high|critical",
  "reversible": true|false,
  "legal_implications": "description of any legal consequences"
}
"""
```

---

## 6. MCP Server Bridge

### 6.1 How Agno Connects to Existing MCP Servers

```python
# agno/tools/mcp_bridge.py
# This is the critical bridge between Agno and the existing TS/Py MCP servers.
# Agno's MCPTools class handles the connection lifecycle.

from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

def get_ts_mcp_tools() -> MCPTools:
    """
    Connects to the TypeScript MCP server via stdio command.
    IMPORTANT: Use command-based (stdio) connection, NOT HTTP/SSE.
    HTTP/SSE transport has reconnection edge cases in Agno as of v1.4.
    """
    return MCPTools(
        server_params=StdioServerParameters(
            command="node",
            args=["mcp-servers/ts-server/dist/index.js"],
            env={"NODE_ENV": "production"}
        )
    )

def get_py_mcp_tools() -> MCPTools:
    """
    Connects to the Python MCP server (includes Semantica tools).
    """
    return MCPTools(
        server_params=StdioServerParameters(
            command="python",
            args=["mcp-servers/py-server/main.py"],
        )
    )

# GOTCHA: MCPTools is an async context manager.
# You MUST use it with `async with` or agents will not receive tools.
# Pattern:
#
#   async with get_ts_mcp_tools() as ts_tools:
#       agent = Agent(tools=[ts_tools], ...)
#       await agent.arun(...)
#
# Do NOT instantiate MCPTools outside of async context.
```

---

## 7. Agent Factory (Constructor Pattern)

```python
# agno/agents/factory.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.knowledge.combined import CombinedKnowledgeBase
from .instructions import (
    PLATFORM_AGENT_INSTRUCTIONS,
    INGEST_AGENT_INSTRUCTIONS,
    ANALYSIS_AGENT_INSTRUCTIONS,
    EVIDENCE_AGENT_INSTRUCTIONS,
    REVIEW_AGENT_INSTRUCTIONS,
)
from ..config.settings import settings

def get_model(provider: str = None, model: str = None):
    """
    Returns the appropriate Agno model instance.
    Falls back to settings defaults if not specified.
    """
    provider = provider or settings.AGNO_DEFAULT_PROVIDER
    model = model or settings.AGNO_DEFAULT_MODEL

    if provider == "openai":
        return OpenAIChat(id=model, api_key=settings.OPENAI_API_KEY)
    elif provider == "anthropic":
        return Claude(id=model, api_key=settings.ANTHROPIC_API_KEY)
    elif provider == "google":
        return Gemini(id=model, api_key=settings.GOOGLE_API_KEY)
    # Add more providers as needed
    raise ValueError(f"Unknown provider: {provider}")

def get_storage():
    return PostgresAgentStorage(
        table_name="agent_sessions",
        db_url=settings.SYNC_DATABASE_URL,
    )

def get_memory():
    return Memory(
        db=PostgresMemoryDb(db_url=settings.SYNC_DATABASE_URL),
        model=get_model(),
    )

def build_platform_agent(
    provider: str = None,
    model: str = None,
    tools: list = None,
) -> Agent:
    return Agent(
        name="PlatformAgent",
        role="MCP Platform Orchestrator",
        model=get_model(provider, model),
        instructions=PLATFORM_AGENT_INSTRUCTIONS,
        storage=get_storage(),
        memory=get_memory(),
        tools=tools or [],
        show_tool_calls=True,
        markdown=True,
        structured_outputs=False,
    )

def build_ingest_agent(tools: list = None) -> Agent:
    return Agent(
        name="IngestAgent",
        role="Evidence Ingest Specialist",
        model=get_model(),
        instructions=INGEST_AGENT_INSTRUCTIONS,
        storage=get_storage(),
        tools=tools or [],
        show_tool_calls=True,
    )

def build_analysis_agent(tools: list = None) -> Agent:
    return Agent(
        name="AnalysisAgent",
        role="Forensic Analysis Specialist",
        model=get_model(),
        instructions=ANALYSIS_AGENT_INSTRUCTIONS,
        storage=get_storage(),
        tools=tools or [],
        show_tool_calls=True,
    )

def build_evidence_agent(tools: list = None) -> Agent:
    return Agent(
        name="EvidenceAgent",
        role="Chain of Custody Specialist",
        model=get_model(),
        instructions=EVIDENCE_AGENT_INSTRUCTIONS,
        storage=get_storage(),
        tools=tools or [],
        show_tool_calls=True,
    )

def build_review_agent(tools: list = None) -> Agent:
    return Agent(
        name="ReviewAgent",
        role="HITL Approval Coordinator",
        model=get_model(),
        instructions=REVIEW_AGENT_INSTRUCTIONS,
        storage=get_storage(),
        tools=tools or [],
        show_tool_calls=True,
    )
```

---

## 8. Configuration

```python
# agno/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    PGVECTOR_DIMENSION: int = 1536

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    # DuckDB
    DUCKDB_PATH: str = "./data/evidence_vault.duckdb"

    # MCP Servers
    MCP_TS_SERVER_COMMAND: str = "node"
    MCP_TS_SERVER_ARGS: str = "mcp-servers/ts-server/dist/index.js"
    MCP_PY_SERVER_COMMAND: str = "python"
    MCP_PY_SERVER_ARGS: str = "mcp-servers/py-server/main.py"

    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_HOST: str = "http://localhost:11434"

    # Defaults
    AGNO_DEFAULT_PROVIDER: str = "openai"
    AGNO_DEFAULT_MODEL: str = "gpt-4o"
    AGNO_FALLBACK_PROVIDER: str = "anthropic"
    AGNO_FALLBACK_MODEL: str = "claude-sonnet-4-5"

    # Evidence
    EVIDENCE_VAULT_PATH: str = "./data/evidence"
    EVIDENCE_HASH_ALGO: str = "sha256"
    CUSTODY_LOG_PATH: str = "./data/custody_log.jsonl"
    WORM_ENABLED: bool = True

    # API
    AGNO_API_HOST: str = "0.0.0.0"
    AGNO_API_PORT: int = 8000
    AGNO_API_SECRET_KEY: str
    HITL_APPROVAL_TIMEOUT_SECONDS: int = 86400

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

---

## 9. FastAPI Entry Point

```python
# agno/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from .config.settings import settings
from .api.routes import router
from .tools.mcp_bridge import get_ts_mcp_tools, get_py_mcp_tools
from .agents.factory import build_platform_agent

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MCP Platform Agno API starting up")
    # Startup: verify database, MCP servers, etc.
    # Add startup checks here
    yield
    logger.info("MCP Platform Agno API shutting down")

app = FastAPI(
    title="MCP Platform — Agno API",
    description="Forensic evidence analysis platform for custody litigation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # client dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

# Run with: uvicorn agno.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 10. API Routes

```python
# agno/api/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

# ─── REQUEST / RESPONSE MODELS ───────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    provider: Optional[str] = None   # override default LLM provider
    model: Optional[str] = None      # override default model

class ChatResponse(BaseModel):
    session_id: str
    response: str
    run_id: str
    tools_called: list[str] = []
    approval_required: bool = False
    approval_id: Optional[str] = None

class IngestRequest(BaseModel):
    file_path: str
    source_type: Optional[str] = None   # auto-detect if not provided
    case_id: Optional[str] = None

class ApprovalRequest(BaseModel):
    approval_id: str
    decision: str   # "approved" or "rejected"
    notes: Optional[str] = None

# ─── ROUTES ──────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint — routes to PlatformAgent."""
    session_id = req.session_id or str(uuid.uuid4())
    # Implementation: instantiate agent with MCP tools, run message
    # See agents/factory.py build_platform_agent()
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.post("/ingest")
async def ingest(req: IngestRequest):
    """Trigger evidence ingestion for a file."""
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Get evidence item with full custody chain."""
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.get("/approvals/pending")
async def get_pending_approvals():
    """Get all pending HITL approval items."""
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.post("/approvals/decide")
async def decide_approval(req: ApprovalRequest):
    """Approve or reject a queued action."""
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.get("/health")
async def health():
    return {"status": "ok", "service": "mcp-platform-agno"}
```

---

## 11. Diagrams

### System Overview

```mermaid
flowchart TD
    U[User / Attorney] --> C[Client React App]
    C --> API[FastAPI :8000]
    API --> PA[PlatformAgent]
    PA --> IA[IngestAgent]
    PA --> AA[AnalysisAgent]
    PA --> EA[EvidenceAgent]
    PA --> RA[ReviewAgent HITL]
    IA --> MCP_TS[TS MCP Server :3001]
    IA --> MCP_PY[Py MCP Server :3002]
    AA --> MCP_PY
    EA --> DB[(PostgreSQL + pgvector)]
    EA --> DDB[(DuckDB Vault)]
    RA --> AQ[(Approval Queue)]
    AQ --> C
    MCP_PY --> NEO[(Neo4j Graph)]
    MCP_PY --> SEM[Semantica AI]
```

### Evidence Ingest Flow

```mermaid
flowchart LR
    F[Raw File] --> H[SHA-256 Hash]
    H --> CL1[Custody Log: ingest]
    CL1 --> DT[Detect Source Type]
    DT --> P{Parser}
    P -->|SMS| PSMS[SMS Parser]
    P -->|Facebook| PFB[FB Parser]
    P -->|iMessage| PIM[iMessage Parser]
    PSMS --> N[Normalize → Schema]
    PFB --> N
    PIM --> N
    N --> CL2[Custody Log: normalized]
    N --> V[(DuckDB Vault)]
    N --> PG[(PostgreSQL)]
    V --> EMB[Embed → pgvector]
    PG --> KG[Neo4j Graph]
```

### HITL Approval Flow

```mermaid
sequenceDiagram
    participant A as Agent
    participant RA as ReviewAgent
    participant AQ as ApprovalQueue DB
    participant U as User UI
    participant Exec as Executor

    A->>RA: request_approval(action, risk_level)
    RA->>AQ: INSERT approval_queue entry
    RA->>U: Notify: "Action pending your approval"
    U->>AQ: GET /approvals/pending
    AQ-->>U: Return pending items
    U->>AQ: POST /approvals/decide {approved}
    AQ-->>RA: Approval received
    RA->>Exec: Execute approved action
    Exec->>AQ: UPDATE status=approved
    Exec->>A: Return result
```

### Chain of Custody State Machine

```mermaid
stateDiagram-v2
    [*] --> RAW : file ingested
    RAW --> HASHED : sha256 computed (ONCE)
    HASHED --> NORMALIZED : parser applied
    NORMALIZED --> ANALYZED : NLP/pattern analysis
    ANALYZED --> REVIEWED : routed to HITL
    REVIEWED --> APPROVED : human approves
    REVIEWED --> REJECTED : human rejects
    APPROVED --> [*] : available for legal submission
    REJECTED --> ANALYZED : re-analyze with notes

    note right of HASHED : sha256 is IMMUTABLE after this state
```

### Agent Team Structure

```mermaid
flowchart TD
    PA[PlatformAgent<br/>Orchestrator] --> IA[IngestAgent]
    PA --> AA[AnalysisAgent]
    PA --> EA[EvidenceAgent]
    PA --> RA[ReviewAgent]
    IA --> T1[MCP Bridge Tools]
    AA --> T1
    AA --> T2[NLP Tools]
    EA --> T3[Custody Tools]
    RA --> T4[Approval Queue Tools]
    T1 --> MCP_TS[TS MCP Server]
    T1 --> MCP_PY[Py + Semantica]
```

### Data Model

```mermaid
erDiagram
    EVIDENCE_ITEMS ||--o{ CUSTODY_LOG : "has chain"
    EVIDENCE_ITEMS ||--o{ APPROVAL_QUEUE : "requires review"
    EVIDENCE_ITEMS ||--o{ KNOWLEDGE_EMBEDDINGS : "vectorized"
    AGENT_RUNS ||--o{ CUSTODY_LOG : "generates"

    EVIDENCE_ITEMS {
        uuid id PK
        string source_type
        string status
        string sha256
        jsonb content_normalized
        timestamptz ingested_at
    }

    CUSTODY_LOG {
        uuid id PK
        uuid evidence_id FK
        timestamptz timestamp
        string action
        string actor
        string sha256_before
        string sha256_after
    }

    APPROVAL_QUEUE {
        uuid id PK
        uuid evidence_id FK
        string status
        string risk_level
        jsonb action_payload
        timestamptz expires_at
    }
```

---

## 12. Implementation Sequence

Work through these stages in order. Do not skip ahead.

- **Stage 1 — Foundation (v0.1.0):** Install dependencies, create `agno/` directory structure, wire `settings.py`, verify PostgreSQL connection, run `agno_schema.sql`, confirm pgvector works. Gate: `GET /health` returns 200.

- **Stage 2 — MCP Bridge (v0.2.0):** Implement `mcp_bridge.py`, connect to TS MCP server via stdio, connect to Py MCP server via stdio, verify tool list is received from each. Gate: `MCPTools.list_tools()` returns tools from both servers.

- **Stage 3 — First Agent (v0.3.0):** Build `IngestAgent` with MCP tools attached, implement SHA-256 hash tool, implement one parser (SMS first — it's already working), write to DuckDB, write to PostgreSQL, record custody_log entry. Gate: One SMS file ingested end-to-end with custody chain.

- **Stage 4 — Platform Agent + API (v0.4.0):** Build `PlatformAgent`, wire `POST /chat` endpoint, wire `POST /ingest` endpoint, connect to client. Gate: User can type a message and get a response via the API.

- **Stage 5 — Analysis + HITL (v0.5.0):** Build `AnalysisAgent` with NLP tools, build `ReviewAgent` with approval queue, implement `GET /approvals/pending` and `POST /approvals/decide`. Gate: Analysis result routed to approval queue, user can approve/reject.

- **Stage 6 — Knowledge Graph + Semantica (v0.6.0):** Wire Neo4j via Py MCP server's Semantica tools, populate entity graph from normalized messages, implement W3C PROV-O provenance records. Gate: Evidence entity visible in Neo4j with provenance URI.

---

## 13. Current State of Primary Files

- **`mcp-servers/ts-server/`** contains ~22 working MCP tools including evidence search, database queries, and file operations. The dist/ output must be compiled before Agno can connect. Run `npm run build` inside ts-server/.

- **`mcp-servers/py-server/`** contains ~25 working MCP tools including Semantica AI integration for knowledge graphs and provenance tracking. Has working SMS parser. Facebook and iMessage parsers are stubs that need Alpha 1 code ported.

- **`docker-compose.yml`** contains existing service definitions for PostgreSQL, Redis, Neo4j, and the client. Do not replace this file — add the Agno API service as an additional entry.

- **`.env.example`** contains existing environment variables. Add Agno-specific variables listed in Section 3 above. Do not remove any existing variables.

- **`migrations/`** contains existing Alembic migrations. Add the Agno schema (`agno_schema.sql`) as a new Alembic migration, do not run it manually.

---

## 14. Instructions for the Coding Agent

### Primary Focus
Implement `agno/` directory from scratch following the scaffolds in this document. Your first commit should be the directory structure with all `__init__.py` files and `settings.py`. Each subsequent commit should pass the stage gate defined in Section 12.

### Do Not Break
- Do not modify any file in `mcp-servers/ts-server/` or `mcp-servers/py-server/` unless explicitly instructed
- Do not replace `docker-compose.yml` — extend it
- Do not replace `.env.example` — extend it
- Do not run `DROP TABLE` on any existing table
- Do not modify `custody_log` table permissions to allow UPDATE or DELETE — it must remain append-only forever

### Running the Application

```bash
# 1. Install Python dependencies
cd agno && pip install -r requirements.txt

# 2. Start infrastructure
docker-compose up -d postgres redis neo4j

# 3. Build TS MCP server
cd mcp-servers/ts-server && npm install && npm run build

# 4. Run Agno migrations
alembic upgrade head

# 5. Start Agno API
uvicorn agno.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Start MCP servers (Agno connects to these via stdio, they start on-demand)
# The MCP bridge in agno/tools/mcp_bridge.py handles startup automatically
```

### Debugging Guidance
- If MCP tools aren't being received by agents: check that the MCP server compiled successfully and the path in `MCP_TS_SERVER_ARGS` is correct relative to where uvicorn is run from (repo root)
- If pgvector errors appear: verify `CREATE EXTENSION IF NOT EXISTS vector;` ran on the database
- If agents return empty responses: check `show_tool_calls=True` in agent constructor and inspect logs for tool call failures
- If custody_log entries are missing: the agent's tool call likely failed silently — check `agent_runs.tools_called` JSONB for the run

### Known Fragile Areas
- **MCP stdio connection:** If the TS or Py MCP server crashes during an agent run, the agent will hang. Implement a health-check wrapper around `MCPTools` startup.
- **Agno MCPTools async context:** Every agent that uses MCP tools must be constructed INSIDE the `async with MCPTools()` block. Constructing agents outside it and passing tools in will result in disconnected tools.
- **pgvector dimension mismatch:** If you change the embedding model, the vector dimension must match `PGVECTOR_DIMENSION` in settings and the column definition. A mismatch causes a silent insert failure.
- **SHA-256 WORM enforcement:** The application code does not have a database-level constraint preventing sha256 updates. The enforcement is purely in agent instructions. A future migration should add a `BEFORE UPDATE` trigger that raises an exception if `sha256` is changed on an already-hashed row.

### Development Process
1. Run the stage gate test before committing each stage
2. Every new tool must be added to `tools/__init__.py` exports
3. Every new agent must be added to `agents/factory.py`
4. Every new API route needs a corresponding Pydantic model in `api/models.py`
5. All database changes go through Alembic — never raw SQL in production

### User / Stakeholder Preferences
- The end user (Matt) does not write code. All agent responses must be in plain English.
- Legal admissibility is the highest priority. When in doubt between speed and correctness, choose correctness.
- Every AI-generated analysis finding must include a confidence score and be marked as "AI assessment, requires human review" until approved through the HITL queue.
- Michigan family court standards apply. Preserve Electronically Stored Information (ESI) rules apply.

---

## 15. Testing Strategy

### Unit Tests
- `test_settings.py` — verify all required env vars load correctly
- `test_custody_tools.py` — verify SHA-256 is computed correctly and stored once
- `test_parsers.py` — verify SMS/Facebook/iMessage parsers produce valid `CommunicationMessage` objects
- `test_agent_factory.py` — verify each agent builds without error for each supported LLM provider

### Integration Tests
- `test_ingest_flow.py` — full ingest of a test SMS file: hash → parse → normalize → vault → postgres → custody_log
- `test_mcp_bridge.py` — verify Agno connects to TS and Py MCP servers and receives tool lists
- `test_approval_queue.py` — verify high-risk action routes to queue, verify approval unblocks action

### E2E / Workflow Tests
- `test_chat_ingest.py` — user sends "ingest this file" → IngestAgent runs → evidence appears in DB
- `test_chat_analysis.py` — user asks "analyze messages from [person]" → AnalysisAgent runs → approval queued → user approves → report returned

### Regression Risks
- Any change to SHA-256 hashing logic must re-run `test_custody_tools.py`
- Any parser change must re-run `test_parsers.py` against the existing test fixtures from Alpha 1
- Any change to `custody_log` table or insert logic must re-run `test_ingest_flow.py`

### Acceptance Criteria (Stage 3 Gate)
- [ ] One SMS test file ingested without error
- [ ] `evidence_items` row created with correct `sha256` and `status="normalized"`
- [ ] `custody_log` has entries for `action="ingest"` and `action="normalized"`
- [ ] `sha256` in `evidence_items` matches manual `sha256sum` of the original file
- [ ] DuckDB vault contains the normalized messages

---

## 16. Deployment / Runtime Notes

### Environment Assumptions
- Development: Local Docker Compose (all services on localhost)
- Python 3.11+
- Node.js 20+ (for TS MCP server)
- All services defined in `docker-compose.yml` must be healthy before starting Agno API

### Secrets / Config
- All secrets in `.env` file at repo root
- Never commit `.env` — it is in `.gitignore`
- Minimum required to start: `DATABASE_URL`, `SYNC_DATABASE_URL`, `AGNO_API_SECRET_KEY`, and at least one LLM provider API key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)

### Build / Run Commands

```bash
# Full stack startup
docker-compose up -d
cd mcp-servers/ts-server && npm run build
uvicorn agno.main:app --reload --port 8000
```

### Monitoring / Logs
- Agno API uses `structlog` — logs are JSON-structured at INFO level by default
- Set `LOG_LEVEL=DEBUG` in `.env` for verbose MCP tool call logging
- `agent_runs` table in PostgreSQL contains a full record of every agent execution
- `custody_log` table is the authoritative audit trail for evidence handling

### Rollback Notes
- All database changes are Alembic migrations — rollback with `alembic downgrade -1`
- The `agno/` directory is additive — removing it does not break existing MCP server functionality
- MCP server code is untouched by Agno integration — they run independently

---

## 17. Open Questions

- **Q1:** The Facebook parser is a stub. Before Stage 3 can use it, the Alpha 1 `MCP_Tool_Platform` repo must be referenced to port the working parser. Confirm location of Alpha 1 parser code.
- **Q2:** The iMessage parser depends on the SQLite backup format from iOS backups. Confirm what file format the test data is in (raw `.db` file, exported `.csv`, or third-party export format) before implementing the parser.
- **Q3:** Semantica AI license/API key — confirm whether the Py MCP server already has valid Semantica credentials in `.env` or if new credentials need to be obtained.

---

## 18. Next Steps (Potential)

- **LiteLLM Proxy Integration:** Add LiteLLM as a unified model proxy in front of all LLM provider calls. This gives a single endpoint to switch providers without changing agent code, adds rate limiting, and enables cost tracking across providers.
- **ContextForge Plugin Pipeline:** Wire ContextForge for PII detection, content moderation, and secrets scanning on all ingested content before it reaches the LLM. This is a hard requirement before any evidence goes to the analysis agent in production.
- **Agno Monitoring Dashboard:** Enable Agno's built-in monitoring if a local deployment is acceptable, or wire `agent_runs` table to a lightweight Grafana dashboard for run visualization.
- **Court Document Export:** Build an `ExportAgent` that takes approved analysis results and generates formatted PDF reports with exhibit numbering, chain of custody appendix, and attorney certification block.
- **LanceDB Hybrid Search:** Add LanceDB alongside pgvector for faster hybrid BM25 + vector search across large message corpora once evidence volume exceeds ~100k messages.

---

## 19. Summary of Updates

**Updates (initial → v1.0.0):**
- **Version Number:** Initial creation — no prior version of this document existed
- **Core Functionality:** Full Agno framework integration plan replacing previously deprecated Conductor OSS ADR
- **Architecture:** Clean-slate Agno + FastAPI + pgvector + Neo4j design with MCP bridge to existing TS/Py servers
- **Instructions:** Complete coding agent handoff with no placeholders — all sections contain implementation-ready defaults
- **Roadmap:** 6-stage implementation sequence with explicit gate criteria per stage
