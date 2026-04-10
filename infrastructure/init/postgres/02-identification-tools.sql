-- =============================================================================
-- AI DIAL Stack — Identification Tools Schema Migration
-- =============================================================================
-- Adds tables for identification and analysis tool outputs.
-- These tables store results from DPK pre-processing, user's custom detection,
-- voice fingerprinting, and behavioral analysis tools.
--
-- Migration: 02-identification-tools.sql
-- Date: 2026-03-15
-- =============================================================================

-- =============================================================================
-- EVIDENCE SCHEMA: Message Analysis Results
-- =============================================================================
-- Stores per-message results from all identification tools.
-- Each message can have multiple analysis rows (different tools, different passes).

CREATE TABLE IF NOT EXISTS evidence.message_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    message_id UUID NOT NULL REFERENCES evidence.messages(id) ON DELETE CASCADE,
    
    -- Analysis metadata
    tool_name VARCHAR(100) NOT NULL,        -- e.g., 'dpk_hap', 'user_darvo', 'fingerprint_voice'
    tool_version VARCHAR(50),               -- Model version for reproducibility
    analysis_pass VARCHAR(20) NOT NULL      -- 'pass1' (blind), 'pass2' (hindsight), 'ad_hoc'
        CHECK (analysis_pass IN ('pass1', 'pass2', 'ad_hoc')),
    analysis_run_id UUID,                   -- Groups analyses from same run
    
    -- DPK HAP results
    hap_score NUMERIC(5,4),                 -- 0-1 toxicity score
    hap_sentence_scores JSONB,              -- Per-sentence scores array
    
    -- PII detection results
    pii_detected JSONB,                     -- [{type, text, start, end, confidence}]
    pii_redacted_text TEXT,                 -- Text with PII replaced
    pii_entity_types TEXT[],                -- ['PERSON', 'EMAIL_ADDRESS', ...]
    
    -- Language & quality
    detected_language VARCHAR(10),          -- ISO language code
    language_confidence NUMERIC(5,4),
    doc_quality_score NUMERIC(5,4),
    readability_metrics JSONB,              -- {flesch_kincaid, grade_level, reading_ease, ...}
    
    -- Voice fingerprinting
    voice_style_features JSONB,             -- {avg_word_length, vocab_richness, ...}
    voice_delta_score NUMERIC(5,4),         -- Burrows' Delta distance
    voice_author_probability NUMERIC(5,4),  -- Probability of same author
    
    -- Behavioral detection (user's custom system)
    behavioral_patterns JSONB,              -- [{pattern_id, name, confidence, evidence_spans}]
    behavioral_severity INT,                -- 1-10 overall severity
    behavioral_confidence NUMERIC(5,4),
    
    -- DARVO detection
    darvo_score NUMERIC(5,4),               -- 0-1 DARVO likelihood
    darvo_role_classification VARCHAR(50),  -- 'victim', 'offender', 'neutral'
    darvo_evidence_spans JSONB,             -- [{text, start, end, type}]
    
    -- Coercive control
    coercive_behaviors JSONB,               -- [{behavior, frequency, severity, evidence}]
    coercive_severity INT,                  -- 1-10
    
    -- Semantica NER results (cached here for quick access)
    extracted_entities JSONB,               -- [{text, type, confidence, start, end}]
    extracted_relations JSONB,              -- [{subject, predicate, object, confidence}]
    
    -- Generic fallback (for tools not covered above)
    raw_results JSONB,                      -- Full tool output as JSON
    
    -- Audit fields (MANDATORY)
    source_hash VARCHAR(64) NOT NULL,       -- SHA-256 of input text
    processing_time_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_ma_message ON evidence.message_analysis(message_id);
CREATE INDEX IF NOT EXISTS idx_ma_tool ON evidence.message_analysis(tool_name);
CREATE INDEX IF NOT EXISTS idx_ma_pass ON evidence.message_analysis(analysis_pass);
CREATE INDEX IF NOT EXISTS idx_ma_run ON evidence.message_analysis(analysis_run_id);
CREATE INDEX IF NOT EXISTS idx_ma_hap ON evidence.message_analysis(hap_score) WHERE hap_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ma_darvo ON evidence.message_analysis(darvo_score) WHERE darvo_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ma_severity ON evidence.message_analysis(behavioral_severity) WHERE behavioral_severity IS NOT NULL;

-- =============================================================================
-- EVIDENCE SCHEMA: Analysis Runs
-- =============================================================================
-- Tracks each analysis run (batch of messages analyzed together)

CREATE TABLE IF NOT EXISTS evidence.analysis_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    run_type VARCHAR(50) NOT NULL,          -- 'ingestion_pass1', 'hindsight_pass2', 'ad_hoc'
    triggered_by VARCHAR(100),              -- 'ingestion_agent', 'analyst', 'scheduled'
    tools_used TEXT[] NOT NULL,             -- ['dpk_hap', 'user_darvo', ...]
    message_count INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'completed', 'failed')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB
);

-- =============================================================================
-- EVIDENCE SCHEMA: Behavioral Findings
-- =============================================================================
-- High-level findings that span multiple messages (patterns, trends)

CREATE TABLE IF NOT EXISTS evidence.behavioral_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    
    -- Finding details
    finding_type VARCHAR(100) NOT NULL,     -- 'darvo_pattern', 'coercive_control', 'gaslighting', etc.
    severity INT NOT NULL CHECK (severity BETWEEN 1 AND 10),
    confidence NUMERIC(5,4) NOT NULL,
    
    -- Evidence
    message_ids UUID[] NOT NULL,            -- Messages supporting this finding
    evidence_spans JSONB,                   -- [{message_id, text, start, end}]
    pattern_description TEXT,
    
    -- MCL mapping
    mcl_factors VARCHAR(50)[],              -- ['(b)', '(c)', '(d)'] — which factors apply
    
    -- Timeline
    first_occurrence TIMESTAMPTZ,
    last_occurrence TIMESTAMPTZ,
    frequency_count INT DEFAULT 1,
    
    -- Review status
    review_status VARCHAR(20) DEFAULT 'pending'
        CHECK (review_status IN ('pending', 'reviewed', 'confirmed', 'dismissed')),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    
    -- Audit
    source_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bf_type ON evidence.behavioral_findings(finding_type);
CREATE INDEX IF NOT EXISTS idx_bf_severity ON evidence.behavioral_findings(severity);
CREATE INDEX IF NOT EXISTS idx_bf_review ON evidence.behavioral_findings(review_status);

-- Trigger for updated_at
CREATE TRIGGER behavioral_findings_updated BEFORE UPDATE ON evidence.behavioral_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA evidence TO dial;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA evidence TO dial;
