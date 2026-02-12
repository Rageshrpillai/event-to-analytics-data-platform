-- warehouse/gold/ddl/02_dim_actors.sql

DROP TABLE IF EXISTS gold.dim_actors CASCADE;

CREATE TABLE gold.dim_actors (
    actor_id            BIGINT PRIMARY KEY, 
    actor_login         VARCHAR(255) NOT NULL, 
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast searches by name
CREATE INDEX idx_dim_actors_login ON gold.dim_actors (actor_login);