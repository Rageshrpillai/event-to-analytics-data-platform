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

DROP VIEW IF EXISTS silver.v_events;

CREATE OR REPLACE VIEW silver.v_events AS
SELECT 
    -- ==========================================================
    -- 1. Identity & Watermark (Keep Raw)
    -- ==========================================================
    event_id,
    event_time,
	COALESCE((event_type), 'unknownEvent') AS event_type,
    processed_at, -- Crucial for Incremental Loading in Gold


    event_time::DATE AS event_date,
    EXTRACT(YEAR FROM event_time)::INT AS event_year,
    EXTRACT(MONTH FROM event_time)::INT AS event_month,
    EXTRACT(DAY FROM event_time)::INT AS event_day,
    EXTRACT(HOUR FROM event_time)::INT AS event_hour, 

    -- 3. Actor Normalization (Defensive) 👤
	actor_id,
    COALESCE((actor_login), 'unknownuser') AS actor_login,
    

    -- org_id stays NULL
    org_id, 
    -- org_login gets a label 
    COALESCE((org_login), 'independent') AS org_login,
	repo_id,
    COALESCE((repo_name), 'unknownrepo') AS repo_name,


   
    -- Forces NULLs to FALSE. 
    COALESCE(is_public, false) AS is_public

FROM silver.events;
