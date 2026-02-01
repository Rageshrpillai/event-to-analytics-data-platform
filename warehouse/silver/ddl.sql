
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.events (
    event_id      VARCHAR(50) PRIMARY KEY,
    event_type    VARCHAR(50),
    actor_id      VARCHAR(50),
    actor_login   TEXT,
    repo_id       VARCHAR(50),
    repo_name     TEXT,
    event_time    TIMESTAMPTZ,
    processed_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);