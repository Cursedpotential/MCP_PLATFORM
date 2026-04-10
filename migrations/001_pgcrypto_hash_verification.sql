-- Migration: Hash Verification Functions
-- Version: 1.0.0
-- Created: 2026-03-16
-- Author: execution@opencode
-- Project: dial-stack
-- Description: PostgreSQL functions for evidence hash verification using pgcrypto

-- ============================================================================
-- SECTION 1: Enable Required Extensions
-- ============================================================================

-- Enable pgcrypto for SHA-256 hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable uuid-ossp for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SECTION 2: Hash Verification Tables
-- ============================================================================

-- Main evidence table (if not exists)
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    original_hash TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    contextforge_tags TEXT[],
    contextforge_metadata JSONB DEFAULT '{}',
    custom_tool_tags TEXT[],
    custom_tool_metadata JSONB DEFAULT '{}',
    verification_status TEXT DEFAULT 'pending',
    hash_algorithm TEXT DEFAULT 'sha256',
    signature TEXT,
    public_key TEXT,
    signed_at TIMESTAMPTZ,
    signer_id TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Hash verification log table
CREATE TABLE IF NOT EXISTS hash_verification_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    evidence_id UUID NOT NULL REFERENCES evidence(id),
    verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('verified', 'failed', 'error')),
    expected_hash TEXT,
    computed_hash TEXT,
    algorithm TEXT DEFAULT 'sha256',
    verifier_id TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create index on evidence_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_hash_verification_log_evidence_id 
ON hash_verification_log(evidence_id);

-- Create index on verified_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_hash_verification_log_verified_at 
ON hash_verification_log(verified_at DESC);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_hash_verification_log_status 
ON hash_verification_log(status);

-- ============================================================================
-- SECTION 3: Hash Verification Functions
-- ============================================================================

-- Function: verify_evidence_hash
-- Description: Verify evidence hash matches stored hash
-- Parameters:
--   p_evidence_id: UUID of the evidence to verify
--   p_content: BYTEA content to hash and compare
-- Returns: TEXT ('VERIFIED', 'FAILED', or error message)
CREATE OR REPLACE FUNCTION verify_evidence_hash(
    p_evidence_id UUID,
    p_content BYTEA
) RETURNS TEXT AS $$
DECLARE
    v_stored_hash TEXT;
    v_computed_hash TEXT;
    v_algorithm TEXT;
    v_result TEXT;
BEGIN
    -- Get stored hash and algorithm
    SELECT original_hash, COALESCE(hash_algorithm, 'sha256')
    INTO v_stored_hash, v_algorithm
    FROM evidence WHERE id = p_evidence_id;
    
    IF v_stored_hash IS NULL THEN
        RETURN 'ERROR: Evidence not found';
    END IF;
    
    -- Compute hash based on algorithm
    v_computed_hash := CASE v_algorithm
        WHEN 'sha256' THEN encode(digest(p_content, 'sha256'), 'hex')
        WHEN 'sha384' THEN encode(digest(p_content, 'sha384'), 'hex')
        WHEN 'sha512' THEN encode(digest(p_content, 'sha512'), 'hex')
        WHEN 'blake2b' THEN encode(digest(p_content, 'blake2b'), 'hex')
        ELSE encode(digest(p_content, 'sha256'), 'hex')
    END;
    
    -- Compare (case-insensitive)
    IF lower(v_stored_hash) = lower(v_computed_hash) THEN
        -- Log successful verification
        INSERT INTO hash_verification_log (
            evidence_id, status, expected_hash, computed_hash, algorithm
        ) VALUES (
            p_evidence_id, 'verified', v_stored_hash, v_computed_hash, v_algorithm
        );
        
        -- Update evidence verification status
        UPDATE evidence 
        SET verification_status = 'verified', updated_at = NOW()
        WHERE id = p_evidence_id;
        
        RETURN 'VERIFIED';
    ELSE
        -- Log failed verification
        INSERT INTO hash_verification_log (
            evidence_id, status, expected_hash, computed_hash, algorithm
        ) VALUES (
            p_evidence_id, 'failed', v_stored_hash, v_computed_hash, v_algorithm
        );
        
        -- Update evidence verification status
        UPDATE evidence 
        SET verification_status = 'failed', updated_at = NOW()
        WHERE id = p_evidence_id;
        
        RETURN 'FAILED: Hash mismatch';
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    -- Log error
    INSERT INTO hash_verification_log (
        evidence_id, status, error_message
    ) VALUES (
        p_evidence_id, 'error', SQLERRM
    );
    
    RETURN 'ERROR: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: compute_evidence_hash
-- Description: Compute hash for content and return it
-- Parameters:
--   p_content: BYTEA content to hash
--   p_algorithm: TEXT algorithm name (default: sha256)
-- Returns: TEXT hash value
CREATE OR REPLACE FUNCTION compute_evidence_hash(
    p_content BYTEA,
    p_algorithm TEXT DEFAULT 'sha256'
) RETURNS TEXT AS $$
BEGIN
    RETURN CASE lower(p_algorithm)
        WHEN 'sha256' THEN encode(digest(p_content, 'sha256'), 'hex')
        WHEN 'sha384' THEN encode(digest(p_content, 'sha384'), 'hex')
        WHEN 'sha512' THEN encode(digest(p_content, 'sha512'), 'hex')
        WHEN 'blake2b' THEN encode(digest(p_content, 'blake2b'), 'hex')
        WHEN 'md5' THEN encode(digest(p_content, 'md5'), 'hex')  -- Legacy
        ELSE encode(digest(p_content, 'sha256'), 'hex')
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;

-- Function: batch_verify_evidence
-- Description: Verify multiple evidence items at once
-- Parameters:
--   p_evidence_ids: UUID[] array of evidence IDs
--   p_contents: BYTEA[] array of contents (must match order)
-- Returns: TABLE with verification results
CREATE OR REPLACE FUNCTION batch_verify_evidence(
    p_evidence_ids UUID[],
    p_contents BYTEA[]
) RETURNS TABLE (
    evidence_id UUID,
    status TEXT,
    stored_hash TEXT,
    computed_hash TEXT
) AS $$
DECLARE
    i INT;
    v_result TEXT;
BEGIN
    -- Validate array lengths match
    IF array_length(p_evidence_ids, 1) != array_length(p_contents, 1) THEN
        RAISE EXCEPTION 'Array lengths must match';
    END IF;
    
    -- Process each item
    FOR i IN 1..array_length(p_evidence_ids, 1) LOOP
        v_result := verify_evidence_hash(p_evidence_ids[i], p_contents[i]);
        
        -- Return result
        RETURN QUERY
        SELECT 
            p_evidence_ids[i] AS evidence_id,
            CASE 
                WHEN v_result = 'VERIFIED' THEN 'verified'
                WHEN v_result LIKE 'FAILED%' THEN 'failed'
                ELSE 'error'
            END AS status,
            e.original_hash AS stored_hash,
            encode(digest(p_contents[i], 'sha256'), 'hex') AS computed_hash
        FROM evidence e
        WHERE e.id = p_evidence_ids[i];
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Function: get_verification_history
-- Description: Get verification history for an evidence item
-- Parameters:
--   p_evidence_id: UUID of the evidence
--   p_limit: INT maximum number of records to return
-- Returns: TABLE with verification history
CREATE OR REPLACE FUNCTION get_verification_history(
    p_evidence_id UUID,
    p_limit INT DEFAULT 10
) RETURNS TABLE (
    id UUID,
    verified_at TIMESTAMPTZ,
    status TEXT,
    expected_hash TEXT,
    computed_hash TEXT,
    algorithm TEXT,
    verifier_id TEXT,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.verified_at,
        h.status,
        h.expected_hash,
        h.computed_hash,
        h.algorithm,
        h.verifier_id,
        h.error_message
    FROM hash_verification_log h
    WHERE h.evidence_id = p_evidence_id
    ORDER BY h.verified_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: get_verification_stats
-- Description: Get verification statistics
-- Returns: TABLE with counts by status
CREATE OR REPLACE FUNCTION get_verification_stats()
RETURNS TABLE (
    total_evidence BIGINT,
    verified_count BIGINT,
    failed_count BIGINT,
    pending_count BIGINT,
    error_count BIGINT,
    verification_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) AS total_evidence,
        COUNT(*) FILTER (WHERE verification_status = 'verified') AS verified_count,
        COUNT(*) FILTER (WHERE verification_status = 'failed') AS failed_count,
        COUNT(*) FILTER (WHERE verification_status = 'pending') AS pending_count,
        COUNT(*) FILTER (WHERE verification_status = 'error') AS error_count,
        ROUND(
            COUNT(*) FILTER (WHERE verification_status = 'verified')::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 
            2
        ) AS verification_rate
    FROM evidence;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 4: Trigger for Auto-Verification on Insert
-- ============================================================================

-- Trigger function to auto-verify on insert
CREATE OR REPLACE FUNCTION auto_verify_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Set initial verification status
    NEW.verification_status := 'pending';
    NEW.created_at := NOW();
    NEW.updated_at := NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists, then create
DROP TRIGGER IF EXISTS trg_evidence_auto_verify ON evidence;
CREATE TRIGGER trg_evidence_auto_verify
    BEFORE INSERT ON evidence
    FOR EACH ROW
    EXECUTE FUNCTION auto_verify_on_insert();

-- ============================================================================
-- SECTION 5: Utility Functions
-- ============================================================================

-- Function: mark_evidence_verified
-- Description: Manually mark evidence as verified
CREATE OR REPLACE FUNCTION mark_evidence_verified(
    p_evidence_id UUID,
    p_verifier_id TEXT DEFAULT 'system'
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE evidence
    SET verification_status = 'verified',
        updated_at = NOW()
    WHERE id = p_evidence_id;
    
    INSERT INTO hash_verification_log (
        evidence_id, status, verifier_id
    ) VALUES (
        p_evidence_id, 'verified', p_verifier_id
    );
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function: mark_evidence_failed
-- Description: Mark evidence as failed verification
CREATE OR REPLACE FUNCTION mark_evidence_failed(
    p_evidence_id UUID,
    p_error_message TEXT DEFAULT NULL,
    p_verifier_id TEXT DEFAULT 'system'
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE evidence
    SET verification_status = 'failed',
        updated_at = NOW()
    WHERE id = p_evidence_id;
    
    INSERT INTO hash_verification_log (
        evidence_id, status, error_message, verifier_id
    ) VALUES (
        p_evidence_id, 'failed', p_error_message, p_verifier_id
    );
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECTION 6: Comments
-- ============================================================================

COMMENT ON TABLE evidence IS 'Main evidence storage with hash verification';
COMMENT ON TABLE hash_verification_log IS 'Audit trail for all hash verifications';
COMMENT ON FUNCTION verify_evidence_hash IS 'Verify evidence content hash against stored hash';
COMMENT ON FUNCTION compute_evidence_hash IS 'Compute hash for content using specified algorithm';
COMMENT ON FUNCTION batch_verify_evidence IS 'Verify multiple evidence items in one call';
COMMENT ON FUNCTION get_verification_history IS 'Get verification history for an evidence item';
COMMENT ON FUNCTION get_verification_stats IS 'Get overall verification statistics';

-- ============================================================================
-- SECTION 7: Grant Permissions (adjust as needed)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE ON evidence TO evidence_app;
-- GRANT SELECT, INSERT ON hash_verification_log TO evidence_app;
-- GRANT EXECUTE ON FUNCTION verify_evidence_hash TO evidence_app;
-- GRANT EXECUTE ON FUNCTION compute_evidence_hash TO evidence_app;
-- GRANT EXECUTE ON FUNCTION batch_verify_evidence TO evidence_app;
-- GRANT EXECUTE ON FUNCTION get_verification_history TO evidence_app;
-- GRANT EXECUTE ON FUNCTION get_verification_stats TO evidence_app;
