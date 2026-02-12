-- warehouse/gold/ddl/03_dim_repos.sql

DROP TABLE IF EXISTS gold.dim_repos CASCADE;

CREATE TABLE gold.dim_repos (
    repo_id             BIGINT PRIMARY KEY,
    
    -- 1. The Full Name (Display)
    repo_name           VARCHAR(255) NOT NULL, -- 'facebook/react'

    -- 2. The Split (Analysis)
    repo_owner          VARCHAR(255),          -- 'facebook'
    repo_project        VARCHAR(255),          -- 'react'
    
    -- 3. Organization Metadata
    org_id              BIGINT,
    org_login           VARCHAR(255),
    
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index the owner so you can instantly find "All Google Repos"
CREATE INDEX idx_dim_repos_owner ON gold.dim_repos (repo_owner);
CREATE INDEX idx_dim_repos_project ON gold.dim_repos (repo_project);