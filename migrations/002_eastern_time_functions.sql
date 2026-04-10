-- Migration: Eastern Time Conversion Functions
-- Version: 1.0.0
-- Created: 2026-03-16
-- Author: execution@opencode
-- Project: dial-stack
-- Description: PostgreSQL functions for Eastern Time conversion with DST handling

-- ============================================================================
-- SECTION 1: Eastern Time Conversion Functions
-- ============================================================================

-- Function: utc_to_eastern
-- Description: Convert UTC timestamp to Eastern Time with DST info
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: TABLE with utc, eastern, is_dst, timezone_name
CREATE OR REPLACE FUNCTION utc_to_eastern(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS TABLE (
    utc_timestamp TIMESTAMPTZ,
    eastern_timestamp TIMESTAMP,
    is_dst BOOLEAN,
    timezone_name TEXT,
    offset_hours INTEGER
) AS $$
DECLARE
    v_eastern TIMESTAMP;
    v_month INTEGER;
    v_day INTEGER;
    v_hour INTEGER;
    v_year INTEGER;
    v_dst_start TIMESTAMP;
    v_dst_end TIMESTAMP;
    v_is_dst BOOLEAN;
BEGIN
    -- Convert to Eastern Time
    v_eastern := p_utc_timestamp AT TIME ZONE 'America/New_York';
    
    -- Extract date components
    v_year := EXTRACT(YEAR FROM v_eastern);
    v_month := EXTRACT(MONTH FROM v_eastern);
    v_day := EXTRACT(DAY FROM v_eastern);
    v_hour := EXTRACT(HOUR FROM v_eastern);
    
    -- Calculate DST dates for the year
    -- DST starts: Second Sunday in March at 2:00 AM local
    -- DST ends: First Sunday in November at 2:00 AM local
    
    -- Find second Sunday in March
    WITH march AS (
        SELECT DATE(v_year || '-03-01') AS first_day
    ),
    first_sunday_march AS (
        SELECT first_day + ((6 - EXTRACT(DOW FROM first_day)::INTEGER + 7) % 7)::INTEGER AS sunday
        FROM march
    )
    SELECT sunday + INTERVAL '7 days' INTO v_dst_start
    FROM first_sunday_march;
    
    -- Find first Sunday in November
    WITH november AS (
        SELECT DATE(v_year || '-11-01') AS first_day
    ),
    first_sunday_november AS (
        SELECT first_day + ((6 - EXTRACT(DOW FROM first_day)::INTEGER + 7) % 7)::INTEGER AS sunday
        FROM november
    )
    SELECT sunday INTO v_dst_end
    FROM first_sunday_november;
    
    -- Add 2:00 AM to transition times
    v_dst_start := v_dst_start + TIME '02:00:00';
    v_dst_end := v_dst_end + TIME '02:00:00';
    
    -- Determine if DST is active
    v_is_dst := v_eastern >= v_dst_start AND v_eastern < v_dst_end;
    
    RETURN QUERY SELECT
        p_utc_timestamp AS utc_timestamp,
        v_eastern AS eastern_timestamp,
        v_is_dst AS is_dst,
        CASE WHEN v_is_dst THEN 'EDT' ELSE 'EST' END AS timezone_name,
        CASE WHEN v_is_dst THEN -4 ELSE -5 END AS offset_hours;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: format_eastern_timestamp
-- Description: Format timestamp in Eastern Time with timezone
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: TEXT formatted string
CREATE OR REPLACE FUNCTION format_eastern_timestamp(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS TEXT AS $$
DECLARE
    v_eastern TIMESTAMP;
    v_is_dst BOOLEAN;
    v_tz_name TEXT;
BEGIN
    -- Get Eastern Time
    v_eastern := p_utc_timestamp AT TIME ZONE 'America/New_York';
    
    -- Determine DST using the utc_to_eastern function
    SELECT is_dst, timezone_name INTO v_is_dst, v_tz_name
    FROM utc_to_eastern(p_utc_timestamp);
    
    -- Format: YYYY-MM-DD HH24:MI:SS TZ (UTC±H)
    RETURN to_char(v_eastern, 'YYYY-MM-DD HH24:MI:SS') || ' ' || v_tz_name;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: format_eastern_timestamp_full
-- Description: Format timestamp with full timezone info
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: TEXT formatted string with UTC offset
CREATE OR REPLACE FUNCTION format_eastern_timestamp_full(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS TEXT AS $$
DECLARE
    v_eastern TIMESTAMP;
    v_is_dst BOOLEAN;
    v_tz_name TEXT;
    v_offset INTEGER;
BEGIN
    -- Get Eastern Time with DST info
    SELECT 
        eastern_timestamp,
        is_dst,
        timezone_name,
        offset_hours
    INTO v_eastern, v_is_dst, v_tz_name, v_offset
    FROM utc_to_eastern(p_utc_timestamp);
    
    -- Format: YYYY-MM-DD HH24:MI:SS TZ (UTC±H)
    RETURN to_char(v_eastern, 'YYYY-MM-DD HH24:MI:SS') || ' ' || v_tz_name || 
           ' (UTC' || CASE WHEN v_offset >= 0 THEN '+' ELSE '' END || v_offset::TEXT || ')';
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: get_dst_transitions
-- Description: Get DST transition dates for a year
-- Parameters:
--   p_year: INTEGER year
-- Returns: TABLE with dst_start and dst_end
CREATE OR REPLACE FUNCTION get_dst_transitions(
    p_year INTEGER
) RETURNS TABLE (
    year INTEGER,
    dst_start TIMESTAMP,
    dst_end TIMESTAMP,
    dst_start_utc TIMESTAMPTZ,
    dst_end_utc TIMESTAMPTZ
) AS $$
DECLARE
    v_dst_start TIMESTAMP;
    v_dst_end TIMESTAMP;
BEGIN
    -- Find second Sunday in March (DST start)
    WITH march AS (
        SELECT DATE(p_year || '-03-01') AS first_day
    ),
    first_sunday_march AS (
        SELECT first_day + ((6 - EXTRACT(DOW FROM first_day)::INTEGER + 7) % 7)::INTEGER AS sunday
        FROM march
    )
    SELECT sunday + INTERVAL '7 days' + TIME '02:00:00' INTO v_dst_start
    FROM first_sunday_march;
    
    -- Find first Sunday in November (DST end)
    WITH november AS (
        SELECT DATE(p_year || '-11-01') AS first_day
    ),
    first_sunday_november AS (
        SELECT first_day + ((6 - EXTRACT(DOW FROM first_day)::INTEGER + 7) % 7)::INTEGER AS sunday
        FROM november
    )
    SELECT sunday + TIME '02:00:00' INTO v_dst_end
    FROM first_sunday_november;
    
    RETURN QUERY SELECT
        p_year AS year,
        v_dst_start AS dst_start,
        v_dst_end AS dst_end,
        v_dst_start AT TIME ZONE 'America/New_York' AT TIME ZONE 'UTC' AS dst_start_utc,
        v_dst_end AT TIME ZONE 'America/New_York' AT TIME ZONE 'UTC' AS dst_end_utc;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 2: Evidence View with Eastern Time
-- ============================================================================

-- View: evidence_with_eastern_time
-- Description: Evidence records with Eastern Time conversion
CREATE OR REPLACE VIEW evidence_with_eastern_time AS
SELECT
    e.id,
    e.original_hash,
    e.file_path,
    e.file_size,
    e.mime_type,
    e.created_at AS created_at_utc,
    e.created_at AT TIME ZONE 'America/New_York' AS created_at_eastern,
    CASE 
        WHEN e.created_at AT TIME ZONE 'America/New_York' >= 
             (SELECT DATE(EXTRACT(YEAR FROM e.created_at)::TEXT || '-03-01') + 
              ((6 - EXTRACT(DOW FROM DATE(EXTRACT(YEAR FROM e.created_at)::TEXT || '-03-01'))::INTEGER + 7) % 7)::INTEGER + 
              INTERVAL '7 days' + TIME '02:00:00')
        AND e.created_at AT TIME ZONE 'America/New_York' <
             (SELECT DATE(EXTRACT(YEAR FROM e.created_at)::TEXT || '-11-01') + 
              ((6 - EXTRACT(DOW FROM DATE(EXTRACT(YEAR FROM e.created_at)::TEXT || '-11-01'))::INTEGER + 7) % 7)::INTEGER + 
              TIME '02:00:00')
        THEN 'EDT'
        ELSE 'EST'
    END AS timezone_name,
    e.contextforge_tags,
    e.custom_tool_tags,
    e.verification_status,
    e.metadata
FROM evidence e;

-- ============================================================================
-- SECTION 3: Helper Functions
-- ============================================================================

-- Function: is_dst_active
-- Description: Check if DST is active for a given timestamp
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: BOOLEAN
CREATE OR REPLACE FUNCTION is_dst_active(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS BOOLEAN AS $$
DECLARE
    v_is_dst BOOLEAN;
BEGIN
    SELECT is_dst INTO v_is_dst FROM utc_to_eastern(p_utc_timestamp);
    RETURN v_is_dst;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: get_eastern_offset
-- Description: Get UTC offset for Eastern Time at a given timestamp
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: INTEGER offset in hours (-5 or -4)
CREATE OR REPLACE FUNCTION get_eastern_offset(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS INTEGER AS $$
DECLARE
    v_offset INTEGER;
BEGIN
    SELECT offset_hours INTO v_offset FROM utc_to_eastern(p_utc_timestamp);
    RETURN v_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: convert_utc_to_eastern_json
-- Description: Convert UTC to Eastern and return as JSON
-- Parameters:
--   p_utc_timestamp: TIMESTAMPTZ timestamp in UTC
-- Returns: JSONB with conversion details
CREATE OR REPLACE FUNCTION convert_utc_to_eastern_json(
    p_utc_timestamp TIMESTAMPTZ
) RETURNS JSONB AS $$
DECLARE
    v_result RECORD;
BEGIN
    SELECT * INTO v_result FROM utc_to_eastern(p_utc_timestamp);
    
    RETURN jsonb_build_object(
        'utc_timestamp', v_result.utc_timestamp,
        'eastern_timestamp', v_result.eastern_timestamp,
        'is_dst', v_result.is_dst,
        'timezone_name', v_result.timezone_name,
        'offset_hours', v_result.offset_hours,
        'eastern_str', to_char(v_result.eastern_timestamp, 'YYYY-MM-DD HH24:MI:SS'),
        'formatted', format_eastern_timestamp_full(p_utc_timestamp)
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 4: Batch Conversion Function
-- ============================================================================

-- Function: batch_convert_to_eastern
-- Description: Convert multiple timestamps to Eastern Time
-- Parameters:
--   p_utc_timestamps: TIMESTAMPTZ[] array of UTC timestamps
-- Returns: TABLE with conversion results
CREATE OR REPLACE FUNCTION batch_convert_to_eastern(
    p_utc_timestamps TIMESTAMPTZ[]
) RETURNS TABLE (
    original_timestamp TIMESTAMPTZ,
    eastern_timestamp TIMESTAMP,
    is_dst BOOLEAN,
    timezone_name TEXT,
    offset_hours INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t AS original_timestamp,
        (t AT TIME ZONE 'America/New_York')::TIMESTAMP AS eastern_timestamp,
        is_dst_active(t) AS is_dst,
        CASE WHEN is_dst_active(t) THEN 'EDT' ELSE 'EST' END AS timezone_name,
        get_eastern_offset(t) AS offset_hours
    FROM unnest(p_utc_timestamps) AS t;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SECTION 5: Comments
-- ============================================================================

COMMENT ON FUNCTION utc_to_eastern IS 'Convert UTC timestamp to Eastern Time with DST info';
COMMENT ON FUNCTION format_eastern_timestamp IS 'Format timestamp in Eastern Time with timezone abbreviation';
COMMENT ON FUNCTION format_eastern_timestamp_full IS 'Format timestamp with full timezone info including UTC offset';
COMMENT ON FUNCTION get_dst_transitions IS 'Get DST transition dates for a year';
COMMENT ON FUNCTION is_dst_active IS 'Check if DST is active for a given timestamp';
COMMENT ON FUNCTION get_eastern_offset IS 'Get UTC offset for Eastern Time at a given timestamp';
COMMENT ON FUNCTION convert_utc_to_eastern_json IS 'Convert UTC to Eastern and return as JSON';
COMMENT ON FUNCTION batch_convert_to_eastern IS 'Convert multiple timestamps to Eastern Time';
COMMENT ON VIEW evidence_with_eastern_time IS 'Evidence records with Eastern Time conversion';

-- ============================================================================
-- SECTION 6: Example Usage
-- ============================================================================

-- Example: Convert current time to Eastern
-- SELECT * FROM utc_to_eastern(NOW());

-- Example: Get DST transitions for 2024
-- SELECT * FROM get_dst_transitions(2024);

-- Example: Format timestamp
-- SELECT format_eastern_timestamp_full(NOW());

-- Example: Batch convert
-- SELECT * FROM batch_convert_to_eastern(ARRAY[NOW(), NOW() - INTERVAL '1 day', NOW() - INTERVAL '6 months']);
