-- *
-- ===============================================================================
-- View: Silver Staging Events (silver.v_events)
-- ===============================================================================
-- Purpose:
--     This view acts as the "Transformation Layer" for the Silver Schema.
--     It cleans, standardizes, and derives useful columns from the raw table
--     without duplicating data on disk.

-- Defensive Logic Applied:
--     . NULL Handling: Replaces NULLs with meaningful defaults ('Independent', 'Unknown').
--     . Date Derivation: Pre-calculates Year, Month, Day for faster analysis.
--     . Payload Removal: Drops the heavy JSON column for performance.
-- */
-- warehouse/silver/view_silver.sql

DROP VIEW IF EXISTS silver.v_events;

CREATE OR REPLACE VIEW silver.v_events AS
SELECT 
    -- 1. Identity & Watermark
    event_id,
    event_time,
    COALESCE(event_type, 'UnknownEvent') AS event_type,
    processed_at, 

    -- 2. Date Derivation (The Smart Key Logic)
    (EXTRACT(YEAR FROM event_time) * 10000 + 
     EXTRACT(MONTH FROM event_time) * 100 + 
     EXTRACT(DAY FROM event_time))::INT AS date_id,
     
    EXTRACT(HOUR FROM event_time)::INT AS event_hour,

    -- 3. Actor Normalization (Safe Cast) 🛡️
    -- Logic: If it's numbers, cast it. If it's garbage ('unknown'), return NULL.
    CASE 
        WHEN actor_id ~ '^[0-9]+$' THEN actor_id::BIGINT 
        ELSE -1
    END AS actor_id,
    
    COALESCE(actor_login, 'unknownuser') AS actor_login,

    -- 4. Repo Normalization (Safe Cast) 🛡️
    CASE 
        WHEN repo_id ~ '^[0-9]+$' THEN repo_id::BIGINT 
        ELSE -1
    END AS repo_id,
    
    COALESCE(repo_name, 'unknownrepo') AS repo_name,

    -- 5. Org Normalization (Safe Cast) 🛡️
    CASE 
        WHEN org_id ~ '^[0-9]+$' THEN org_id::BIGINT 
        ELSE NULL 
    END AS org_id,
    
    COALESCE(org_login, 'independent') AS org_login,

    -- 6. Flags
    COALESCE(is_public, true) AS is_public

FROM silver.events;