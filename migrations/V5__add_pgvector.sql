CREATE EXTENSION IF NOT EXISTS vector;

-- HNSW used instead of IVFFlat — no minimum row requirement,
-- works on an empty table, better recall at low data volumes.
-- Switch to IVFFlat with lists=200 once you have 10k+ chunks.
CREATE INDEX IF NOT EXISTS idx_log_chunks_embedding
    ON log_chunks USING hnsw (embedding vector_cosine_ops);