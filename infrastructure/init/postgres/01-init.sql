-- =============================================================================
-- AI DIAL Stack — Unified PostgreSQL Init Script
-- =============================================================================
-- Consolidates ALL tables from the legacy architecture into a single PG:
--   - Former MySQL "Tier 6" app tables (users, apiKeys, llmProviders, patterns...)
--   - Former PostgreSQL "Tier 5" evidence tables (messages, conversations, documents)
--   - Human-in-the-loop review queue (from entity_match_candidates)
--
-- Image: pgvector/pgvector:pg16
-- Extensions: pgvector, pg_trgm, uuid-ossp, citext
-- =============================================================================

-- =============================================================================
-- DATABASES
-- =============================================================================
-- The default POSTGRES_DB is 'dial' (app + evidence).
-- Keycloak needs its own isolated database to avoid table conflicts.

SELECT 'CREATE DATABASE keycloak OWNER dial'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID v4 generation
CREATE EXTENSION IF NOT EXISTS "vector";       -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- Trigram fuzzy matching
CREATE EXTENSION IF NOT EXISTS "citext";       -- Case-insensitive text

-- =============================================================================
-- UUIDv7 FUNCTION (Timestamp-sortable UUIDs)
-- =============================================================================

CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS uuid AS $$
DECLARE
  unix_ts_ms bytea;
  uuid_bytes bytea;
BEGIN
  unix_ts_ms = substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000))::bytea, 3, 6);
  uuid_bytes = decode(encode(gen_random_bytes(10), 'hex'), 'hex');
  uuid_bytes = set_bit(set_bit(unix_ts_ms || uuid_bytes, 48, 0), 49, 1);
  RETURN encode(uuid_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;

-- =============================================================================
-- SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS app;       -- Application metadata (formerly MySQL)
CREATE SCHEMA IF NOT EXISTS evidence;  -- Forensic evidence data

-- =============================================================================
-- UPDATED_AT TRIGGER FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- APP SCHEMA: Users & Authentication (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.users (
    id SERIAL PRIMARY KEY,
    open_id VARCHAR(64) NOT NULL UNIQUE,
    name TEXT,
    email CITEXT,
    login_method VARCHAR(64),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'analyst')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_signed_in TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.api_keys (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(16) NOT NULL,
    permissions JSONB NOT NULL DEFAULT '["read"]',
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.api_key_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    api_key_id INT NOT NULL REFERENCES app.api_keys(id) ON DELETE CASCADE,
    tool_name VARCHAR(255),
    method VARCHAR(50),
    status_code INT,
    latency_ms INT,
    tokens_used INT,
    cost_cents INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP SCHEMA: LLM Providers & Routing (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.llm_providers (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    provider_name VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    base_url VARCHAR(512),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    priority INT NOT NULL DEFAULT 0,
    usage_count INT NOT NULL DEFAULT 0,
    total_cost_cents INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.routing_rules (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,
    primary_provider_id INT NOT NULL REFERENCES app.llm_providers(id) ON DELETE CASCADE,
    fallback_provider_id INT REFERENCES app.llm_providers(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP SCHEMA: System Prompts & Workflows (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.system_prompts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tool_name VARCHAR(255),
    prompt_text TEXT NOT NULL,
    variables JSONB,
    version INT NOT NULL DEFAULT 1,
    parent_id INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    success_rate INT DEFAULT 0,
    avg_latency_ms INT DEFAULT 0,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.workflow_templates (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    steps JSONB NOT NULL,
    system_prompt_id INT REFERENCES app.system_prompts(id),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP SCHEMA: Behavioral Patterns & Analysis (from init/mysql/01-schema.sql)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.behavioral_patterns (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES app.users(id) ON DELETE CASCADE,
    pattern_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    pattern TEXT NOT NULL,
    description TEXT,
    severity INT NOT NULL DEFAULT 5,
    severity_weight NUMERIC(3,2) DEFAULT 1.0,
    mcl_factors JSONB,
    examples TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    match_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bp_category ON app.behavioral_patterns(category);
CREATE INDEX IF NOT EXISTS idx_bp_severity ON app.behavioral_patterns(severity_weight);

CREATE TABLE IF NOT EXISTS app.pattern_categories (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES app.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    icon VARCHAR(50),
    parent_category_id INT REFERENCES app.pattern_categories(id),
    default_severity INT NOT NULL DEFAULT 5,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.mcl_factors (
    id SERIAL PRIMARY KEY,
    factor_letter VARCHAR(5) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    keywords JSONB,
    pattern_categories JSONB,
    weight NUMERIC(3,2) DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP SCHEMA: HurtLex Lexicon (from init/mysql/01-schema.sql)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.hurtlex_categories (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES app.users(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    term_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.hurtlex_terms (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES app.users(id) ON DELETE CASCADE,
    term VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    level VARCHAR(20),
    pos VARCHAR(20),
    severity NUMERIC(3,2) DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    match_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ht_term ON app.hurtlex_terms(term);
CREATE INDEX IF NOT EXISTS idx_ht_category ON app.hurtlex_terms(category);

-- =============================================================================
-- APP SCHEMA: Analysis & Settings (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.analysis_modules (
    id SERIAL PRIMARY KEY,
    module_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL,
    subcategory VARCHAR(100),
    module_type VARCHAR(50),
    is_built_in BOOLEAN NOT NULL DEFAULT TRUE,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    severity_weight INT DEFAULT 50,
    mcl_mapping VARCHAR(50),
    config JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.severity_weights (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES app.users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    weight INT NOT NULL DEFAULT 5,
    description TEXT,
    mcl_factors JSONB,
    escalation_threshold INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app.user_settings (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, setting_key)
);

-- =============================================================================
-- APP SCHEMA: Human-in-the-Loop Review Queue
-- (from entity_match_candidates in init/mysql/01-schema.sql)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    review_type VARCHAR(50) NOT NULL DEFAULT 'entity_merge',
    -- Entity merge fields
    entity_a TEXT,
    entity_b TEXT,
    confidence NUMERIC(5,4),
    match_method VARCHAR(50) DEFAULT 'jaro_winkler',
    sample_data_a JSONB,
    sample_data_b JSONB,
    -- Generic review fields
    tool_name VARCHAR(255),
    tool_output JSONB,
    context JSONB,
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'COMMITTED')),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    committed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rq_status ON app.review_queue(status);
CREATE INDEX IF NOT EXISTS idx_rq_type ON app.review_queue(review_type);

-- =============================================================================
-- APP SCHEMA: Audit Log (DIAL interceptor request/response pairs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deployment  TEXT,
    model       TEXT,
    user_sub    TEXT,
    request_id  TEXT,
    -- Request fields
    req_messages    JSONB,
    req_tools       JSONB,
    req_stream      BOOLEAN,
    req_temperature FLOAT,
    -- Response fields
    resp_status     INT,
    resp_choices    JSONB,
    resp_usage      JSONB,
    resp_model      TEXT,
    duration_ms     INT,
    -- Error tracking
    error_message   TEXT
);

CREATE INDEX IF NOT EXISTS idx_al_logged_at   ON app.audit_log(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_al_deployment  ON app.audit_log(deployment);
CREATE INDEX IF NOT EXISTS idx_al_user_sub    ON app.audit_log(user_sub);
CREATE INDEX IF NOT EXISTS idx_al_request_id  ON app.audit_log(request_id);


-- =============================================================================
-- APP SCHEMA: Evidence Chain Metadata (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.evidence_chains (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    evidence_id VARCHAR(64),
    original_filename VARCHAR(512) NOT NULL,
    original_hash VARCHAR(64) NOT NULL,
    mime_type VARCHAR(128),
    file_size BIGINT,
    chain_data JSONB NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT TRUE,
    verification_errors TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ec_evidence_id ON app.evidence_chains(evidence_id);
CREATE INDEX IF NOT EXISTS idx_ec_original_hash ON app.evidence_chains(original_hash);

CREATE TABLE IF NOT EXISTS app.evidence_master_index (
    id SERIAL PRIMARY KEY,
    source_hash VARCHAR(64) NOT NULL,
    evidence_id VARCHAR(36) NOT NULL,
    original_filename VARCHAR(1024) NOT NULL,
    tier VARCHAR(16) NOT NULL,
    storage_path TEXT,
    creation_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_emi_evidence_id ON app.evidence_master_index(evidence_id);
CREATE INDEX IF NOT EXISTS idx_emi_source_hash ON app.evidence_master_index(source_hash);
CREATE INDEX IF NOT EXISTS idx_emi_tier ON app.evidence_master_index(tier);

-- =============================================================================
-- APP SCHEMA: Forensic Results (from drizzle/schema.ts)
-- =============================================================================

CREATE TABLE IF NOT EXISTS app.forensic_results (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    case_id VARCHAR(64),
    evidence_id VARCHAR(64),
    source_hash VARCHAR(64),
    source_type VARCHAR(50),
    analysis_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    results JSONB,
    match_count INT DEFAULT 0,
    severity_score INT,
    mcl_factors_matched JSONB,
    confidence INT,
    processing_time_ms INT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- EVIDENCE SCHEMA: Messages (primary evidence store)
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    sender TEXT NOT NULL,
    recipient TEXT,
    body TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    platform TEXT NOT NULL,
    direction TEXT NOT NULL,
    message_type TEXT NOT NULL DEFAULT 'text',
    content_hash TEXT NOT NULL,
    device_id TEXT,
    sender_normalized TEXT,
    recipient_normalized TEXT,
    external_id TEXT,
    raw_data JSONB,
    attachments JSONB,
    provenance JSONB,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(content_hash, device_id, conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_msg_conversation ON evidence.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_msg_sender ON evidence.messages(sender);
CREATE INDEX IF NOT EXISTS idx_msg_content_hash ON evidence.messages(content_hash);
CREATE INDEX IF NOT EXISTS idx_msg_platform ON evidence.messages(platform);
CREATE INDEX IF NOT EXISTS idx_msg_timestamp ON evidence.messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_msg_body_fts ON evidence.messages USING GIN(to_tsvector('english', body));
-- pgvector index for semantic search
CREATE INDEX IF NOT EXISTS idx_msg_embedding ON evidence.messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =============================================================================
-- EVIDENCE SCHEMA: Conversations
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform TEXT NOT NULL,
    participants TEXT[] NOT NULL,
    message_count INT DEFAULT 0,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    last_message TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_participants ON evidence.conversations USING GIN(participants);

-- =============================================================================
-- EVIDENCE SCHEMA: Documents (ingested files)
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    file_size BIGINT,
    file_type TEXT,
    source_platform TEXT,
    acquisition_method TEXT,
    acquired_by TEXT,
    acquisition_date TIMESTAMPTZ,
    processing_status TEXT DEFAULT 'pending',
    message_count INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- EVIDENCE SCHEMA: Hash Audit Trail
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.hash_audit (
    id BIGSERIAL PRIMARY KEY,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    message_count INT,
    status TEXT,
    details JSONB
);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER users_updated BEFORE UPDATE ON app.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER api_keys_updated BEFORE UPDATE ON app.api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER llm_providers_updated BEFORE UPDATE ON app.llm_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER system_prompts_updated BEFORE UPDATE ON app.system_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER review_queue_updated BEFORE UPDATE ON app.review_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER messages_updated BEFORE UPDATE ON evidence.messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER conversations_updated BEFORE UPDATE ON evidence.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER documents_updated BEFORE UPDATE ON evidence.documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- SEED: Default Admin User
-- =============================================================================

INSERT INTO app.users (open_id, name, email, role)
VALUES ('admin-default', 'Admin', 'admin@localhost', 'admin')
ON CONFLICT (open_id) DO NOTHING;

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA app TO dial;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA app TO dial;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA evidence TO dial;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA evidence TO dial;
GRANT USAGE ON SCHEMA app TO dial;
GRANT USAGE ON SCHEMA evidence TO dial;
