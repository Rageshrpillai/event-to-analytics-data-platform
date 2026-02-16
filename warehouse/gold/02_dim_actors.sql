-- warehouse/gold/ddl/02_dim_actors.sql
-- ============================================================
-- Dimension: GitHub Actors (Users)
-- SCD Type: Type 1 (overwrite - no history tracking)
-- ============================================================

DROP TABLE IF EXISTS gold.dim_actors CASCADE;

CREATE TABLE gold.dim_actors (
    -- Business Key
    actor_id            BIGINT PRIMARY KEY, 
    
    -- Attributes
    actor_login         VARCHAR(255) NOT NULL, 
    
    -- ETL Metadata
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_event_time     TIMESTAMPTZ
);

-- ============================================================
-- Indexes
-- ============================================================

-- Enforce uniqueness and enable fast lookups
CREATE  INDEX idx_dim_actors_login ON gold.dim_actors (actor_login);

-- ============================================================
-- Seed Sentinel Value
-- ============================================================

INSERT INTO gold.dim_actors (actor_id, actor_login, last_event_time) VALUES
(-1, 'unknownuser', '1970-01-01'::TIMESTAMPTZ)
ON CONFLICT (actor_id) DO NOTHING;

-- ============================================================
-- Documentation
-- ============================================================

COMMENT ON TABLE gold.dim_actors IS 
'Dimension: GitHub actors (users) - Type 1 SCD with late-arriving data protection';

COMMENT ON COLUMN gold.dim_actors.actor_id IS 
'Primary key: GitHub user ID';

COMMENT ON COLUMN gold.dim_actors.actor_login IS 
'GitHub username (unique, current value)';

COMMENT ON COLUMN gold.dim_actors.updated_at IS 
'ETL operational timestamp - when this row was last touched (for monitoring)';

COMMENT ON COLUMN gold.dim_actors.last_event_time IS 
'Business timestamp - when the latest event for this actor occurred (prevents old data overwrites)';