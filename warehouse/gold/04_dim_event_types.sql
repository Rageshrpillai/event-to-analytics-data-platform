-- warehouse/gold/ddl/04_dim_event_types.sql

-- ============================================================
-- Dimension: Event Types with Auto-Discovery Support
-- ============================================================
DROP TABLE IF EXISTS gold.dim_event_types CASCADE;

CREATE TABLE gold.dim_event_types (
    -- Primary Key
    event_type          VARCHAR(50) PRIMARY KEY,
    
    -- Business Logic (Categorization)
    event_category      VARCHAR(50) NOT NULL,     -- 'Core Activity', 'Engagement', 'Unknown'
    event_label         VARCHAR(100) NOT NULL,    
    event_description   TEXT,
    
    is_core_metric      BOOLEAN DEFAULT FALSE,    -- TRUE for high-value actions (Push, Star)
    
    -- Maintenance Flags (Auto-Discovery)
    is_curated          BOOLEAN DEFAULT FALSE,    -- TRUE = We manually categorized it. FALSE = Auto-discovered.
    discovered_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast grouping by Category
CREATE INDEX idx_dim_event_types_category ON gold.dim_event_types (event_category);

-- Index to find un-curated events (Maintenance Queue)
CREATE INDEX idx_dim_event_types_uncurated ON gold.dim_event_types (is_curated) WHERE is_curated = FALSE;


-- ============================================================
--  SEED DATA (Known Event Types)
-- ============================================================
-- New ones will be added by the ETL script as 'Unknown'.

INSERT INTO gold.dim_event_types 
(event_type, event_category, event_label, event_description, is_core_metric, is_curated) 
VALUES
-- Core Activity (The High Value Actions)
('PushEvent',           'Core Activity', 'Push',         'Code pushed to repository',      TRUE,  TRUE),
('WatchEvent',          'Core Activity', 'Star',         'Repository starred',             TRUE,  TRUE),
('ForkEvent',           'Core Activity', 'Fork',         'Repository forked',              TRUE,  TRUE),
('PullRequestEvent',    'Core Activity', 'Pull Request', 'PR opened/closed/merged',        TRUE,  TRUE),

-- Issue Activity
('IssuesEvent',         'Issue Activity', 'Issue',       'Issue opened/closed',            TRUE,  TRUE),

-- Engagement (Community Interaction)
('IssueCommentEvent',             'Engagement', 'Issue Comment',      'Comment on issue',           FALSE, TRUE),
('PullRequestReviewEvent',        'Engagement', 'PR Review',          'PR reviewed',                FALSE, TRUE),
('PullRequestReviewCommentEvent', 'Engagement', 'PR Review Comment',  'Comment on PR review',       FALSE, TRUE),
('CommitCommentEvent',            'Engagement', 'Commit Comment',     'Comment on commit',          FALSE, TRUE),
('DiscussionEvent',               'Engagement', 'Discussion',         'Discussion activity',        FALSE, TRUE),
('DiscussionCommentEvent',        'Engagement', 'Discussion Comment', 'Comment on discussion',      FALSE, TRUE),

-- Repo Management (Admin Tasks)
('CreateEvent',         'Repo Management', 'Create',      'Branch/tag created',             FALSE, TRUE),
('DeleteEvent',         'Repo Management', 'Delete',      'Branch/tag deleted',             FALSE, TRUE),
('ReleaseEvent',        'Repo Management', 'Release',     'Release published',              FALSE, TRUE),
('MemberEvent',         'Repo Management', 'Member',      'Collaborator added',             FALSE, TRUE),

-- Other
('GollumEvent',         'Other', 'Wiki Edit',    'Wiki page edited',                       FALSE, TRUE),
('PublicEvent',         'Other', 'Made Public',  'Repository made public',                 FALSE, TRUE)

ON CONFLICT (event_type) DO UPDATE 
SET 
    event_category = EXCLUDED.event_category,
    event_label = EXCLUDED.event_label,
    is_core_metric = EXCLUDED.is_core_metric,
    is_curated = TRUE;