-- warehouse/gold/ddl/03_dim_repos.sql

DROP TABLE IF EXISTS gold.dim_repos CASCADE;

CREATE TABLE gold.dim_repos (
    repo_id             BIGINT PRIMARY KEY,
    repo_name           VARCHAR(255) NOT NULL,
    repo_owner          VARCHAR(255),
    repo_project        VARCHAR(255),
    org_id              BIGINT,
    org_login           VARCHAR(255),
    updated_at          TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, 
    last_event_time     TIMESTAMPTZ
);

CREATE INDEX idx_dim_repos_name ON gold.dim_repos (repo_name);
CREATE INDEX idx_dim_repos_owner ON gold.dim_repos (repo_owner);
CREATE INDEX idx_dim_repos_project ON gold.dim_repos (repo_project);

INSERT INTO gold.dim_repos (
    repo_id, repo_name, repo_owner, repo_project, org_login, last_event_time
) VALUES (
    -1, 'unknownrepo', 'unknownowner', 'unknownproject', 'Unknown', '1970-01-01'::TIMESTAMPTZ
)
ON CONFLICT (repo_id) DO NOTHING;