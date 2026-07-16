CREATE TABLE IF NOT EXISTS failures (
    id               VARCHAR(36) PRIMARY KEY,
    build_id         VARCHAR(36) REFERENCES builds(id) ON DELETE CASCADE,
    failure_type     VARCHAR(50),
    confidence       FLOAT,
    evidence_lines   JSONB,
    agent_status     VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    pr_url           VARCHAR(500),
    llm_provider_used VARCHAR(50),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_failures_build_id     ON failures(build_id);
CREATE INDEX IF NOT EXISTS idx_failures_failure_type ON failures(failure_type);
CREATE INDEX IF NOT EXISTS idx_failures_agent_status ON failures(agent_status);