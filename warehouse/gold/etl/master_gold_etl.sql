-- warehouse/gold/etl/master_gold_etl.sql
-- ============================================================
-- Gold ETL: All-or-Nothing Transaction with Performance Timing
-- Industrial Standard Pattern
-- ============================================================

BEGIN;  -- ← Start transaction

-- ========================================
-- Step 1: Load Dimensions
-- ========================================
DO $$
DECLARE
    v_watermark TIMESTAMPTZ;
    v_start_time TIMESTAMPTZ;
    v_end_time TIMESTAMPTZ;
    v_total_start TIMESTAMPTZ;
    v_actors_count INTEGER;
    v_repos_count INTEGER;
    v_types_count INTEGER;
    v_events_count INTEGER;
BEGIN
    -- Record overall start time
    v_total_start := CLOCK_TIMESTAMP();
    
    -- Get watermark from fact table (shared watermark)
    SELECT COALESCE(MAX(silver_processed_at), '1970-01-01'::TIMESTAMPTZ)
    INTO v_watermark
    FROM gold.fact_events;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'GOLD ETL STARTED';
    RAISE NOTICE 'Watermark: %', v_watermark;
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    
    -- ========================================
    -- Load dim_actors
    -- ========================================
    v_start_time := CLOCK_TIMESTAMP();
    
    INSERT INTO gold.dim_actors (actor_id, actor_login, last_event_time)
    SELECT DISTINCT ON (actor_id)
        actor_id,
        actor_login,
        event_time
    FROM silver.v_events
    WHERE processed_at > v_watermark
      AND actor_id != -1
    ORDER BY actor_id, event_time DESC
    ON CONFLICT (actor_id) DO UPDATE SET
        actor_login = EXCLUDED.actor_login,
        last_event_time = EXCLUDED.last_event_time,
        updated_at = CURRENT_TIMESTAMP
    WHERE dim_actors.last_event_time < EXCLUDED.last_event_time;
    
    GET DIAGNOSTICS v_actors_count = ROW_COUNT;
    v_end_time := CLOCK_TIMESTAMP();
    
    RAISE NOTICE '[1/4] dim_actors: % rows | Duration: % ms', 
        v_actors_count,
        EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time))::INTEGER;
    
    -- ========================================
    -- Load dim_repos
    -- ========================================
    v_start_time := CLOCK_TIMESTAMP();
    
    INSERT INTO gold.dim_repos (
        repo_id, repo_name, repo_owner, repo_project, org_id, org_login, last_event_time
    )
    SELECT DISTINCT ON (repo_id)
        repo_id,
        repo_name,
        CASE 
            WHEN repo_name LIKE '%/%' 
             AND LENGTH(repo_name) - LENGTH(REPLACE(repo_name, '/', '')) = 1
            THEN SPLIT_PART(repo_name, '/', 1)
            ELSE 'unknownowner'
        END AS repo_owner,
        CASE 
            WHEN repo_name LIKE '%/%' 
             AND LENGTH(repo_name) - LENGTH(REPLACE(repo_name, '/', '')) = 1
            THEN SPLIT_PART(repo_name, '/', 2)
            ELSE 'unknownproject'
        END AS repo_project,
        org_id,
        org_login,
        event_time
    FROM silver.v_events
    WHERE processed_at > v_watermark
      AND repo_id != -1
    ORDER BY repo_id, event_time DESC
    ON CONFLICT (repo_id) DO UPDATE SET
        repo_name = EXCLUDED.repo_name,
        repo_owner = EXCLUDED.repo_owner,
        repo_project = EXCLUDED.repo_project,
        org_id = EXCLUDED.org_id,
        org_login = EXCLUDED.org_login,
        last_event_time = EXCLUDED.last_event_time,
        updated_at = CURRENT_TIMESTAMP
    WHERE dim_repos.last_event_time < EXCLUDED.last_event_time;  
    
    GET DIAGNOSTICS v_repos_count = ROW_COUNT;
    v_end_time := CLOCK_TIMESTAMP();
    
    RAISE NOTICE '[2/4] dim_repos: % rows | Duration: % ms',
        v_repos_count,
        EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time))::INTEGER;
    
    -- ========================================
    -- Auto-discover event types
    -- ========================================
    v_start_time := CLOCK_TIMESTAMP();
    
    INSERT INTO gold.dim_event_types (
        event_type, event_category, event_label, is_core_metric, is_curated, discovered_at
    )
    SELECT DISTINCT
        event_type,
        'Unknown',
        event_type,
        FALSE,
        FALSE,
        CURRENT_TIMESTAMP
    FROM silver.v_events
    WHERE event_type NOT IN (SELECT event_type FROM gold.dim_event_types)
      AND event_type != 'UnknownEvent'
    ON CONFLICT (event_type) DO NOTHING;
    
    GET DIAGNOSTICS v_types_count = ROW_COUNT;
    v_end_time := CLOCK_TIMESTAMP();
    
    RAISE NOTICE '[3/4] dim_event_types: % new types | Duration: % ms',
        v_types_count,
        EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time))::INTEGER;
    
    -- ========================================
    -- Load Fact Table
    -- ========================================
    v_start_time := CLOCK_TIMESTAMP();
    
    INSERT INTO gold.fact_events (
        event_id, date_id, repo_id, actor_id, event_type,
        event_time, event_hour, is_public, silver_processed_at
    )
    SELECT 
        event_id,
        date_id,
        repo_id,
        actor_id,
        event_type,
        event_time,
        event_hour,
        is_public,
        processed_at AS silver_processed_at
    FROM silver.v_events
    WHERE processed_at > v_watermark
    ON CONFLICT (event_id) DO NOTHING;
    
    GET DIAGNOSTICS v_events_count = ROW_COUNT;
    v_end_time := CLOCK_TIMESTAMP();
    
    RAISE NOTICE '[4/4] fact_events: % rows | Duration: % ms',
        v_events_count,
        EXTRACT(MILLISECONDS FROM (v_end_time - v_start_time))::INTEGER;
    
    -- ========================================
    -- Final Report
    -- ========================================
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ETL SUCCESS - Committing transaction';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total Counts:';
    RAISE NOTICE '  dim_actors:      % total rows', (SELECT COUNT(*) FROM gold.dim_actors);
    RAISE NOTICE '  dim_repos:       % total rows', (SELECT COUNT(*) FROM gold.dim_repos);
    RAISE NOTICE '  dim_event_types: % total rows', (SELECT COUNT(*) FROM gold.dim_event_types);
    RAISE NOTICE '  fact_events:     % total rows', (SELECT COUNT(*) FROM gold.fact_events);
    RAISE NOTICE '';
    RAISE NOTICE 'Batch Summary:';
    RAISE NOTICE '  Actors processed:  %', v_actors_count;
    RAISE NOTICE '  Repos processed:   %', v_repos_count;
    RAISE NOTICE '  Events processed:  %', v_events_count;
    RAISE NOTICE '';
    RAISE NOTICE 'New watermark: %', (SELECT MAX(silver_processed_at) FROM gold.fact_events);
    RAISE NOTICE 'Total duration: % ms', 
        EXTRACT(MILLISECONDS FROM (CLOCK_TIMESTAMP() - v_total_start))::INTEGER;
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    
END $$;

COMMIT;  -- ← All changes saved together

-- If ANY error occurs above, PostgreSQL automatically does:
-- ROLLBACK;  -- ← All changes discarded, nothing saved
