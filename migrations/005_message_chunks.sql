-- =============================================================================
-- Migration 005: Message Chunks Table
-- =============================================================================
-- Adds an evidence.message_chunks table to store chunked message fragments
-- for embedding. Each chunk carries its own SHA-256 hash, UUIDv7 ID, and a
-- pgvector embedding column so that semantic search can operate at the
-- sub-message level.
--
-- Depends on: 001 (pgcrypto), extensions (vector, uuid-ossp)
-- =============================================================================

-- =============================================================================
-- COMMON TRIGGER FUNCTION
-- =============================================================================
-- Define update_updated_at() here so the migration is self-contained and does
-- not depend on the Docker init SQL. Using CREATE OR REPLACE ensures this is
-- idempotent and won't fail if the function already exists.

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MESSAGE CHUNKS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence.message_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    message_id UUID NOT NULL REFERENCES evidence.messages(id) ON DELETE CASCADE,
    ingestion_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_hash TEXT NOT NULL,
    chunk_index INT NOT NULL DEFAULT 0,
    chunk_total INT NOT NULL DEFAULT 1,
    start_offset INT NOT NULL DEFAULT 0,
    end_offset INT NOT NULL DEFAULT 0,
    embedding vector(768),
    embedding_status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common access patterns
CREATE INDEX IF NOT EXISTS idx_chunk_message ON evidence.message_chunks(message_id);
CREATE INDEX IF NOT EXISTS idx_chunk_ingestion ON evidence.message_chunks(ingestion_id);
CREATE INDEX IF NOT EXISTS idx_chunk_hash ON evidence.message_chunks(chunk_hash);
CREATE INDEX IF NOT EXISTS idx_chunk_embedding_status ON evidence.message_chunks(embedding_status);

-- pgvector index for semantic search at chunk level
CREATE INDEX IF NOT EXISTS idx_chunk_embedding ON evidence.message_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search on chunk text
CREATE INDEX IF NOT EXISTS idx_chunk_fts ON evidence.message_chunks
    USING GIN(to_tsvector('english', chunk_text));

-- updated_at trigger
CREATE TRIGGER message_chunks_updated
    BEFORE UPDATE ON evidence.message_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Add message_chunks to the allowlist comment for documentation
COMMENT ON TABLE evidence.message_chunks IS
  'Chunked message fragments for sub-message embedding and vector search. Each chunk has its own SHA-256 hash and pgvector embedding.';
