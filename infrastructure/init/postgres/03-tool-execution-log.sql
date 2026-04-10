-- =============================================================================
-- AI DIAL Stack — Tool Execution Log
-- =============================================================================
-- Logs EVERY tool call: what ran, what it touched, what it produced.
-- This is the single source of truth for all tool execution.
--
-- Migration: 03-tool-execution-log.sql
-- Date: 2026-03-15
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.tool_execution_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    
    -- What ran
    tool_name VARCHAR(100) NOT NULL,
    tool_version VARCHAR(50),
    server VARCHAR(50) NOT NULL,           -- 'py-mcp-server', 'ts-mcp-server', 'js-mcp-server'
    
    -- When
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INT,
    
    -- What it touched (inputs)
    input_hash VARCHAR(64) NOT NULL,       -- SHA-256 of input
    input_summary TEXT,                     -- Human-readable summary of input (truncated)
    input_message_ids UUID[],              -- Messages this tool operated on
    
    -- What it produced (outputs)
    output_hash VARCHAR(64),               -- SHA-256 of output
    output_summary TEXT,                    -- Human-readable summary of output (truncated)
    
    -- What databases/tables it touched
    tables_read TEXT[],                     -- ['evidence.messages', 'app.behavioral_patterns']
    tables_written TEXT[],                  -- ['evidence.message_analysis']
    
    -- What files it touched
    files_read TEXT[],                      -- ['/data/evidence/sms_export.xml']
    files_written TEXT[],                   -- ['/data/analysis/output.json']
    
    -- Result
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('success', 'error', 'timeout', 'skipped')),
    error_message TEXT,
    error_traceback TEXT,
    
    -- Result data (for quick access without joining)
    result_score NUMERIC(5,4),             -- Primary score if tool produces one
    result_category VARCHAR(50),           -- Primary category if tool produces one
    result_entities_found INT DEFAULT 0,   -- Count of entities/items found
    
    -- Provenance
    source_hash VARCHAR(64),               -- Hash of original evidence (if applicable)
    parent_execution_id UUID,              -- If called by a workflow, link to parent
    
    -- Metadata
    metadata JSONB,                        -- Any additional context
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tel_tool ON evidence.tool_execution_log(tool_name);
CREATE INDEX IF NOT EXISTS idx_tel_status ON evidence.tool_execution_log(status);
CREATE INDEX IF NOT EXISTS idx_tel_started ON evidence.tool_execution_log(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_tel_input_hash ON evidence.tool_execution_log(input_hash);
CREATE INDEX IF NOT EXISTS idx_tel_messages ON evidence.tool_execution_log USING GIN(input_message_ids);
CREATE INDEX IF NOT EXISTS idx_tel_tables_read ON evidence.tool_execution_log USING GIN(tables_read);
CREATE INDEX IF NOT EXISTS idx_tel_tables_written ON evidence.tool_execution_log USING GIN(tables_written);
CREATE INDEX IF NOT EXISTS idx_tel_parent ON evidence.tool_execution_log(parent_execution_id);

-- =============================================================================
-- View: Recent Tool Executions (for monitoring dashboard)
-- =============================================================================

CREATE OR REPLACE VIEW evidence.v_recent_tool_executions AS
SELECT 
    id,
    tool_name,
    server,
    started_at,
    duration_ms,
    status,
    input_hash,
    input_summary,
    output_summary,
    tables_read,
    tables_written,
    result_score,
    result_category,
    result_entities_found,
    error_message,
    metadata
FROM evidence.tool_execution_log
ORDER BY started_at DESC
LIMIT 1000;

-- =============================================================================
-- View: Tool Performance Summary
-- =============================================================================

CREATE OR REPLACE VIEW evidence.v_tool_performance AS
SELECT 
    tool_name,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE status = 'success') as success_count,
    COUNT(*) FILTER (WHERE status = 'error') as error_count,
    ROUND(AVG(duration_ms)) as avg_duration_ms,
    MIN(duration_ms) as min_duration_ms,
    MAX(duration_ms) as max_duration_ms,
    MAX(started_at) as last_called_at
FROM evidence.tool_execution_log
GROUP BY tool_name
ORDER BY total_calls DESC;

-- =============================================================================
-- View: Error Log (for debugging)
-- =============================================================================

CREATE OR REPLACE VIEW evidence.v_tool_errors AS
SELECT 
    id,
    tool_name,
    started_at,
    error_message,
    error_traceback,
    input_hash,
    input_summary,
    tables_read,
    metadata
FROM evidence.tool_execution_log
WHERE status = 'error'
ORDER BY started_at DESC;

-- =============================================================================
-- PERMISSIONS
-- =============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA evidence TO dial;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA evidence TO dial;
