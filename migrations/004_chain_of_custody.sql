-- Migration: Chain of Custody with Ed25519 Signatures
-- Version: 1.0.0
-- Created: 2026-03-16
-- Author: execution@opencode
-- Project: dial-stack
-- Description: PostgreSQL tables for cryptographic chain of custody

-- ============================================================================
-- SECTION 1: Signature Storage
-- ============================================================================

-- Store Ed25519 signatures
CREATE TABLE IF NOT EXISTS evidence_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    evidence_id UUID NOT NULL,
    signature TEXT NOT NULL,
    public_key TEXT NOT NULL,
    signed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    signed_hash TEXT NOT NULL,
    signer_id TEXT NOT NULL,
    action TEXT NOT NULL DEFAULT 'created' CHECK (action IN ('created', 'accessed', 'modified', 'transferred', 'verified', 'exported', 'archived')),
    algorithm TEXT DEFAULT 'Ed25519',
    metadata JSONB DEFAULT '{}',
    verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('valid', 'invalid', 'error', 'pending')),
    verified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_evidence_signatures_evidence_id ON evidence_signatures(evidence_id);
CREATE INDEX IF NOT EXISTS idx_evidence_signatures_signer ON evidence_signatures(signer_id);
CREATE INDEX IF NOT EXISTS idx_evidence_signatures_signed_at ON evidence_signatures(signed_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_signatures_action ON evidence_signatures(action);

-- ============================================================================
-- SECTION 2: Chain of Custody
-- ============================================================================

-- Chain of custody entries
CREATE TABLE IF NOT EXISTS chain_of_custody (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    evidence_id UUID NOT NULL,
    sequence_number INTEGER NOT NULL,
    action TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    signature_id UUID NOT NULL REFERENCES evidence_signatures(id),
    previous_hash TEXT,
    entry_hash TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(evidence_id, sequence_number)
);

CREATE INDEX IF NOT EXISTS idx_chain_of_custody_evidence_id ON chain_of_custody(evidence_id);
CREATE INDEX IF NOT EXISTS idx_chain_of_custody_sequence ON chain_of_custody(evidence_id, sequence_number);

-- ============================================================================
-- SECTION 3: Keypair Registry
-- ============================================================================

-- Registry of authorized public keys (optional, for multi-signer scenarios)
CREATE TABLE IF NOT EXISTS authorized_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    public_key TEXT NOT NULL UNIQUE,
    key_name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_authorized_keys_public_key ON authorized_keys(public_key);
CREATE INDEX IF NOT EXISTS idx_authorized_keys_owner ON authorized_keys(owner_id);

-- ============================================================================
-- SECTION 4: Functions
-- ============================================================================

-- Function: Record signature
CREATE OR REPLACE FUNCTION record_signature(
    p_evidence_id UUID,
    p_signature TEXT,
    p_public_key TEXT,
    p_signed_hash TEXT,
    p_signer_id TEXT,
    p_action TEXT DEFAULT 'created',
    p_metadata JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO evidence_signatures (
        evidence_id, signature, public_key, signed_hash, signer_id, action, metadata
    ) VALUES (
        p_evidence_id, p_signature, p_public_key, p_signed_hash, p_signer_id, p_action, p_metadata
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Add chain of custody entry
CREATE OR REPLACE FUNCTION add_custody_entry(
    p_evidence_id UUID,
    p_action TEXT,
    p_actor_id TEXT,
    p_signature_id UUID,
    p_notes TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_sequence_number INTEGER;
    v_previous_hash TEXT;
    v_entry_hash TEXT;
    v_id UUID;
BEGIN
    -- Get next sequence number
    SELECT COALESCE(MAX(sequence_number), 0) + 1
    INTO v_sequence_number
    FROM chain_of_custody
    WHERE evidence_id = p_evidence_id;
    
    -- Get previous entry hash
    SELECT entry_hash INTO v_previous_hash
    FROM chain_of_custody
    WHERE evidence_id = p_evidence_id AND sequence_number = v_sequence_number - 1;
    
    -- Compute entry hash
    v_entry_hash := encode(digest(
        v_sequence_number::TEXT || 
        p_evidence_id::TEXT || 
        p_action || 
        NOW()::TEXT ||
        COALESCE(v_previous_hash, ''),
        'sha256'
    ), 'hex');
    
    -- Insert entry
    INSERT INTO chain_of_custody (
        evidence_id, sequence_number, action, actor_id, signature_id,
        previous_hash, entry_hash, notes
    ) VALUES (
        p_evidence_id, v_sequence_number, p_action, p_actor_id, p_signature_id,
        v_previous_hash, v_entry_hash, p_notes
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get chain of custody
CREATE OR REPLACE FUNCTION get_custody_chain(
    p_evidence_id UUID
) RETURNS TABLE (
    sequence_number INTEGER,
    action TEXT,
    actor_id TEXT,
    timestamp TIMESTAMPTZ,
    signature TEXT,
    public_key TEXT,
    previous_hash TEXT,
    entry_hash TEXT,
    notes TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.sequence_number,
        c.action,
        c.actor_id,
        c.timestamp,
        s.signature,
        s.public_key,
        c.previous_hash,
        c.entry_hash,
        c.notes
    FROM chain_of_custody c
    JOIN evidence_signatures s ON c.signature_id = s.id
    WHERE c.evidence_id = p_evidence_id
    ORDER BY c.sequence_number;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Verify chain integrity
CREATE OR REPLACE FUNCTION verify_custody_chain(
    p_evidence_id UUID
) RETURNS TABLE (
    is_valid BOOLEAN,
    total_entries INTEGER,
    errors TEXT[]
) AS $$
DECLARE
    v_entry RECORD;
    v_prev_hash TEXT;
    v_computed_hash TEXT;
    v_errors TEXT[] := '{}';
    v_is_valid BOOLEAN := true;
    v_total INTEGER;
BEGIN
    -- Check each entry
    FOR v_entry IN
        SELECT * FROM chain_of_custody
        WHERE evidence_id = p_evidence_id
        ORDER BY sequence_number
    LOOP
        -- Verify hash chain
        IF v_entry.sequence_number > 1 THEN
            IF v_entry.previous_hash IS NULL OR v_entry.previous_hash != v_prev_hash THEN
                v_errors := array_append(v_errors, 
                    'Entry ' || v_entry.sequence_number || ': Chain broken');
                v_is_valid := false;
            END IF;
        END IF;
        
        v_prev_hash := v_entry.entry_hash;
    END LOOP;
    
    SELECT COUNT(*) INTO v_total
    FROM chain_of_custody
    WHERE evidence_id = p_evidence_id;
    
    RETURN QUERY SELECT v_is_valid, v_total, v_errors;
END;
$$ LANGUAGE plpgsql;

-- Function: Get signature history
CREATE OR REPLACE FUNCTION get_signature_history(
    p_evidence_id UUID,
    p_limit INTEGER DEFAULT 10
) RETURNS TABLE (
    id UUID,
    signed_at TIMESTAMPTZ,
    action TEXT,
    signer_id TEXT,
    verification_status TEXT,
    algorithm TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.signed_at,
        s.action,
        s.signer_id,
        s.verification_status,
        s.algorithm
    FROM evidence_signatures s
    WHERE s.evidence_id = p_evidence_id
    ORDER BY s.signed_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 5: Update Evidence Table
-- ============================================================================

-- Add signature columns to evidence table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'evidence' AND column_name = 'signature'
    ) THEN
        ALTER TABLE evidence ADD COLUMN signature TEXT;
        ALTER TABLE evidence ADD COLUMN public_key TEXT;
        ALTER TABLE evidence ADD COLUMN signed_at TIMESTAMPTZ;
        ALTER TABLE evidence ADD COLUMN signer_id TEXT;
    END IF;
END $$;

-- ============================================================================
-- SECTION 6: Comments
-- ============================================================================

COMMENT ON TABLE evidence_signatures IS 'Ed25519 signatures for evidence integrity';
COMMENT ON TABLE chain_of_custody IS 'Cryptographic chain of custody entries';
COMMENT ON TABLE authorized_keys IS 'Registry of authorized signing keys';
COMMENT ON FUNCTION record_signature IS 'Record a new signature';
COMMENT ON FUNCTION add_custody_entry IS 'Add entry to chain of custody';
COMMENT ON FUNCTION get_custody_chain IS 'Get full chain of custody for evidence';
COMMENT ON FUNCTION verify_custody_chain IS 'Verify chain integrity';
COMMENT ON FUNCTION get_signature_history IS 'Get signature history for evidence';
