CREATE TABLE IF NOT EXISTS agent_traces (
    id          VARCHAR(36) PRIMARY KEY,
    failure_id  VARCHAR(36) NOT NULL
                    REFERENCES failures(id) ON DELETE CASCADE,
    step_index  INT         NOT NULL,
    thought     TEXT,
    tool_name   VARCHAR(50),
    tool_input  TEXT,
    tool_output TEXT,
    llm_provider VARCHAR(50),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_traces_failure_id
    ON agent_traces(failure_id);
CREATE INDEX IF NOT EXISTS idx_agent_traces_step
    ON agent_traces(failure_id, step_index);