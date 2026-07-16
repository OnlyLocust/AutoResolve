CREATE TABLE IF NOT EXISTS builds (
    id               VARCHAR(36)  PRIMARY KEY,
    repo_name        VARCHAR(255) NOT NULL,
    commit_sha       VARCHAR(40)  NOT NULL,
    workflow_name    VARCHAR(255) NOT NULL,
    workflow_run_id  VARCHAR(50)  UNIQUE,
    logs_url         VARCHAR(500),
    status           VARCHAR(50)  NOT NULL DEFAULT 'RECEIVED',
    log_size_bytes   BIGINT,
    triggered_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_builds_repo_name  ON builds(repo_name);
CREATE INDEX IF NOT EXISTS idx_builds_status     ON builds(status);
CREATE INDEX IF NOT EXISTS idx_builds_created_at ON builds(created_at DESC);