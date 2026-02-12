-- warehouse/gold/ddl/05_fact_events.sql

-- ============================================================
-- Fact Table: GitHub Events (The Core Transaction Table)
-- ============================================================
DROP TABLE IF EXISTS gold.fact_events CASCADE;

CREATE TABLE gold.fact_events (
    -- 1. Identity (Unique Event)
    event_id            VARCHAR(50) PRIMARY KEY,

    -- 2. Foreign Keys (Links to Dimensions)
    -- These enforce that data MUST exist in dimensions first!
    date_id             INT NOT NULL REFERENCES gold.dim_date(date_id),
    repo_id             BIGINT NOT NULL REFERENCES gold.dim_repos(repo_id),
    actor_id            BIGINT NOT NULL REFERENCES gold.dim_actors(actor_id),
    event_type          VARCHAR(50) NOT NULL REFERENCES gold.dim_event_types(event_type),
    
    -- 3. Metrics & Context (The Data)
    event_hour          INT CHECK (event_hour >= 0 AND event_hour <= 23),
    event_time          TIMESTAMPTZ NOT NULL, 
    is_public           BOOLEAN DEFAULT TRUE,

    -- This prevents the "Time Travel" bug.
    silver_processed_at TIMESTAMPTZ NOT NULL, 
    gold_loaded_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Indexes for Dashboard Speed ⚡
-- ============================================================

-- Foreign Key Indexes (Vital for Joins)
CREATE INDEX idx_fact_events_date ON gold.fact_events(date_id);
CREATE INDEX idx_fact_events_repo ON gold.fact_events(repo_id);
CREATE INDEX idx_fact_events_actor ON gold.fact_events(actor_id);
CREATE INDEX idx_fact_events_type ON gold.fact_events(event_type);

-- Time Indexes (For "Last 24 Hours" queries)
CREATE INDEX idx_fact_events_time ON gold.fact_events(event_time);

-- Watermark Index (For Incremental Loading)
CREATE INDEX idx_fact_events_watermark ON gold.fact_events(silver_processed_at);