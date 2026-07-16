CREATE TABLE IF NOT EXISTS log_chunks (
    id           VARCHAR(36)  PRIMARY KEY,
    build_id     VARCHAR(36)  NOT NULL
                     REFERENCES builds(id) ON DELETE CASCADE,
    chunk_index  INT          NOT NULL,
    total_chunks INT          NOT NULL,
    content      TEXT         NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_log_chunks_build_id
    ON log_chunks(build_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_log_chunks_build_chunk
    ON log_chunks(build_id, chunk_index);

-- embedding column added in V5 after pgvector extension is enabled