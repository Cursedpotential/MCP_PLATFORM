-- Migration: Deleted Message Recovery Storage
-- Version: 1.0.0
-- Created: 2026-03-16
-- Author: execution@opencode
-- Project: dial-stack
-- Description: PostgreSQL tables for storing recovered deleted messages from WAL files

-- ============================================================================
-- SECTION 1: WAL File Tracking
-- ============================================================================

-- Track parsed WAL files
CREATE TABLE IF NOT EXISTS wal_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    wal_path TEXT NOT NULL UNIQUE,
    database_path TEXT,
    total_frames INTEGER DEFAULT 0,
    parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    parse_success BOOLEAN DEFAULT false,
    header_magic INTEGER,
    page_size INTEGER,
    checkpoint_seq INTEGER,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_wal_files_path ON wal_files(wal_path);
CREATE INDEX IF NOT EXISTS idx_wal_files_parsed_at ON wal_files(parsed_at DESC);

-- ============================================================================
-- SECTION 2: WAL Frames
-- ============================================================================

-- Store parsed WAL frames
CREATE TABLE IF NOT EXISTS wal_frames (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    wal_file_id UUID NOT NULL REFERENCES wal_files(id),
    frame_offset INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    is_commit BOOLEAN DEFAULT false,
    page_data_hash TEXT NOT NULL,
    page_data_size INTEGER,
    parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(wal_file_id, frame_offset)
);

CREATE INDEX IF NOT EXISTS idx_wal_frames_wal_file ON wal_frames(wal_file_id);
CREATE INDEX IF NOT EXISTS idx_wal_frames_page_number ON wal_frames(page_number);

-- ============================================================================
-- SECTION 3: Recovered Messages
-- ============================================================================

-- Store recovered deleted messages
CREATE TABLE IF NOT EXISTS recovered_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    wal_frame_id UUID NOT NULL REFERENCES wal_frames(id),
    recovery_hash TEXT NOT NULL,
    recovery_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'recovered' CHECK (status IN ('recovered', 'partial', 'failed', 'encrypted')),
    platform TEXT CHECK (platform IN ('ios', 'android', 'unknown')),
    
    -- Extracted message data
    message_text TEXT,
    phone_numbers TEXT[],
    timestamps TEXT[],
    raw_data_preview TEXT,
    
    -- Chain of custody
    original_hash TEXT,
    verification_status TEXT DEFAULT 'pending',
    verified_at TIMESTAMPTZ,
    
    -- Metadata
    extraction_method TEXT DEFAULT 'heuristic',
    confidence_score DECIMAL(3,2),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_recovered_messages_wal_frame ON recovered_messages(wal_frame_id);
CREATE INDEX IF NOT EXISTS idx_recovered_messages_status ON recovered_messages(status);
CREATE INDEX IF NOT EXISTS idx_recovered_messages_recovery_timestamp ON recovered_messages(recovery_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_recovered_messages_phone ON recovered_messages USING GIN(phone_numbers);

-- ============================================================================
-- SECTION 4: Functions
-- ============================================================================

-- Function: Record WAL file parse
CREATE OR REPLACE FUNCTION record_wal_parse(
    p_wal_path TEXT,
    p_database_path TEXT DEFAULT NULL,
    p_total_frames INTEGER DEFAULT 0,
    p_parse_success BOOLEAN DEFAULT false,
    p_header_magic INTEGER DEFAULT NULL,
    p_page_size INTEGER DEFAULT NULL,
    p_checkpoint_seq INTEGER DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO wal_files (
        wal_path, database_path, total_frames, parse_success,
        header_magic, page_size, checkpoint_seq
    ) VALUES (
        p_wal_path, p_database_path, p_total_frames, p_parse_success,
        p_header_magic, p_page_size, p_checkpoint_seq
    )
    ON CONFLICT (wal_path) DO UPDATE SET
        total_frames = EXCLUDED.total_frames,
        parse_success = EXCLUDED.parse_success,
        parsed_at = NOW()
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Record WAL frame
CREATE OR REPLACE FUNCTION record_wal_frame(
    p_wal_file_id UUID,
    p_frame_offset INTEGER,
    p_page_number INTEGER,
    p_is_commit BOOLEAN,
    p_page_data_hash TEXT,
    p_page_data_size INTEGER
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO wal_frames (
        wal_file_id, frame_offset, page_number, is_commit,
        page_data_hash, page_data_size
    ) VALUES (
        p_wal_file_id, p_frame_offset, p_page_number, p_is_commit,
        p_page_data_hash, p_page_data_size
    )
    ON CONFLICT (wal_file_id, frame_offset) DO UPDATE SET
        page_data_hash = EXCLUDED.page_data_hash,
        parsed_at = NOW()
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Record recovered message
CREATE OR REPLACE FUNCTION record_recovered_message(
    p_wal_frame_id UUID,
    p_recovery_hash TEXT,
    p_status TEXT DEFAULT 'recovered',
    p_platform TEXT DEFAULT 'unknown',
    p_message_text TEXT DEFAULT NULL,
    p_phone_numbers TEXT[] DEFAULT NULL,
    p_timestamps TEXT[] DEFAULT NULL,
    p_raw_data_preview TEXT DEFAULT NULL,
    p_extraction_method TEXT DEFAULT 'heuristic',
    p_confidence_score DECIMAL DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO recovered_messages (
        wal_frame_id, recovery_hash, status, platform,
        message_text, phone_numbers, timestamps, raw_data_preview,
        extraction_method, confidence_score
    ) VALUES (
        p_wal_frame_id, p_recovery_hash, p_status, p_platform,
        p_message_text, p_phone_numbers, p_timestamps, p_raw_data_preview,
        p_extraction_method, p_confidence_score
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get recovery statistics
CREATE OR REPLACE FUNCTION get_recovery_stats()
RETURNS TABLE (
    total_wal_files BIGINT,
    total_frames BIGINT,
    total_messages BIGINT,
    recovered_count BIGINT,
    partial_count BIGINT,
    failed_count BIGINT,
    ios_count BIGINT,
    android_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM wal_files)::BIGINT AS total_wal_files,
        (SELECT COUNT(*) FROM wal_frames)::BIGINT AS total_frames,
        (SELECT COUNT(*) FROM recovered_messages)::BIGINT AS total_messages,
        (SELECT COUNT(*) FROM recovered_messages WHERE status = 'recovered')::BIGINT AS recovered_count,
        (SELECT COUNT(*) FROM recovered_messages WHERE status = 'partial')::BIGINT AS partial_count,
        (SELECT COUNT(*) FROM recovered_messages WHERE status = 'failed')::BIGINT AS failed_count,
        (SELECT COUNT(*) FROM recovered_messages WHERE platform = 'ios')::BIGINT AS ios_count,
        (SELECT COUNT(*) FROM recovered_messages WHERE platform = 'android')::BIGINT AS android_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Search messages by phone number
CREATE OR REPLACE FUNCTION search_messages_by_phone(
    p_phone TEXT
) RETURNS TABLE (
    id UUID,
    message_text TEXT,
    phone_numbers TEXT[],
    recovery_timestamp TIMESTAMPTZ,
    platform TEXT,
    wal_path TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rm.id,
        rm.message_text,
        rm.phone_numbers,
        rm.recovery_timestamp,
        rm.platform,
        wf.wal_path
    FROM recovered_messages rm
    JOIN wal_frames wfr ON rm.wal_frame_id = wfr.id
    JOIN wal_files wf ON wfr.wal_file_id = wf.id
    WHERE p_phone = ANY(rm.phone_numbers)
       OR EXISTS (
           SELECT 1 FROM unnest(rm.phone_numbers) AS phone
           WHERE phone LIKE '%' || p_phone || '%'
       )
    ORDER BY rm.recovery_timestamp DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 5: Comments
-- ============================================================================

COMMENT ON TABLE wal_files IS 'Tracks parsed WAL files for forensic analysis';
COMMENT ON TABLE wal_frames IS 'Stores parsed WAL frames with page data';
COMMENT ON TABLE recovered_messages IS 'Recovered deleted messages from WAL parsing';
COMMENT ON FUNCTION record_wal_parse IS 'Record a WAL file parse result';
COMMENT ON FUNCTION record_wal_frame IS 'Record a parsed WAL frame';
COMMENT ON FUNCTION record_recovered_message IS 'Record a recovered deleted message';
COMMENT ON FUNCTION get_recovery_stats IS 'Get recovery statistics';
COMMENT ON FUNCTION search_messages_by_phone IS 'Search messages by phone number';
