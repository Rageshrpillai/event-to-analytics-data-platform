CREATE SCHEMA IF NOT EXISTS bronze;

-- 1. Raw Events Table
CREATE TABLE IF NOT EXISTS bronze.raw_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT,
    full_json JSONB,             
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Dead Letter Queue (For failed inserts)
CREATE TABLE IF NOT EXISTS bronze.dead_letter_queue (
    failed_payload JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);



