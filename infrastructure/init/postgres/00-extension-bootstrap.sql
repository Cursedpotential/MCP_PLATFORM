-- =============================================================================
-- AI DIAL Stack — PostgreSQL Extension Bootstrap
-- =============================================================================
-- Enables built-in and optional extensions only when the extension is available
-- in the current PostgreSQL image. This keeps init idempotent across local dev,
-- WSL/podman, and production while still making the intended capabilities
-- explicit.

CREATE OR REPLACE FUNCTION public.enable_extension_if_available(ext_name TEXT)
RETURNS VOID AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_available_extensions
        WHERE name = ext_name
    ) THEN
        EXECUTE format('CREATE EXTENSION IF NOT EXISTS %I', ext_name);
    ELSE
        RAISE NOTICE 'Extension % is not available in this PostgreSQL image; skipping.', ext_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Core forensic/runtime extensions
SELECT public.enable_extension_if_available('pgcrypto');
SELECT public.enable_extension_if_available('uuid-ossp');
SELECT public.enable_extension_if_available('vector');
SELECT public.enable_extension_if_available('pg_trgm');
SELECT public.enable_extension_if_available('citext');
SELECT public.enable_extension_if_available('unaccent');
SELECT public.enable_extension_if_available('fuzzystrmatch');
SELECT public.enable_extension_if_available('btree_gin');
SELECT public.enable_extension_if_available('btree_gist');

-- Geospatial/custom type support
SELECT public.enable_extension_if_available('postgis');
SELECT public.enable_extension_if_available('postgis_topology');

-- Built-in FDWs
SELECT public.enable_extension_if_available('postgres_fdw');
SELECT public.enable_extension_if_available('file_fdw');

-- Optional federated storage/search extensions
SELECT public.enable_extension_if_available('duckdb_fdw');
SELECT public.enable_extension_if_available('neo4j_fdw');
SELECT public.enable_extension_if_available('parquet_fdw');
SELECT public.enable_extension_if_available('mysql_fdw');
SELECT public.enable_extension_if_available('pg_search');

DROP FUNCTION public.enable_extension_if_available(TEXT);
