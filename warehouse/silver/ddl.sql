-- ============================================================
-- SILVER LAYER DDL (Optimized)
-- Description: Creates the Table and the 7 Critical Indexes
-- ============================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- 1. Reset Table
DROP TABLE IF EXISTS silver.events CASCADE;

-- 2. Create the Table
CREATE TABLE silver.events (
    
    event_id        VARCHAR(50) PRIMARY KEY,
    event_type      VARCHAR(50),

    -- Extracted Columns
    actor_id        VARCHAR(50),
    actor_login     TEXT,
    repo_id         VARCHAR(50),
    repo_name       TEXT,
    org_id          VARCHAR(50),
    org_login       TEXT,

    -- Metadata
    event_time      TIMESTAMPTZ,
    is_public       BOOLEAN DEFAULT TRUE,
    payload         JSONB,
    
    -- Audit Timestamp (The Heartbeat of Incremental Load)
    processed_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. INDEX STRATEGY 
-- ============================================================

-- A. ETL INDEXES (For Dimension Building)
-- Speeds up: SELECT DISTINCT actor_id FROM silver...
CREATE INDEX idx_silver_actor_id ON silver.events (actor_id);
CREATE INDEX idx_silver_repo_id  ON silver.events (repo_id);

-- B. FILTER INDEXES (For Dashboards & Exploration)
CREATE INDEX idx_silver_actor_login ON silver.events (actor_login);
CREATE INDEX idx_silver_repo_name   ON silver.events (repo_name);
CREATE INDEX idx_silver_event_type  ON silver.events (event_type);

-- C. TIMELINE INDEXES (For History & Incremental Load)
CREATE INDEX idx_silver_event_time   ON silver.events (event_time);
-- Speeds up: WHERE processed_at > {last_run} (Incremental ETL)
CREATE INDEX idx_silver_processed_at ON silver.events (processed_at);

-- ============================================================
-- D. MONITORING
-- ============================================================
/*
SELECT schemaname, indexname, idx_scan 
FROM pg_stat_user_indexes 
WHERE schemaname = 'silver' AND idx_scan = 0;
*/