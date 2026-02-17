import sys
import json
import psycopg2    
import logging    
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime

# --- PATH SETUP ---
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from config import Config
from logger import get_logger



#  it uses the default "pipeline.log"
pipeline_logger = get_logger("SILVER_JOB") 

#log_filename="silver.log" to override the default.
silver_logger = get_logger("SILVER_DATA", level=logging.DEBUG, log_filename="silver.log")



#Mute Console for Silver Data
for handler in silver_logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler):
        silver_logger.removeHandler(handler)

BATCH_SIZE = 5000

# ============================================================
# 1. FETCH QUERY
# ============================================================
FETCH_UNPROCESSED = """
    SELECT full_json
    FROM bronze.raw_events b
    WHERE NOT EXISTS (
        SELECT 1 FROM silver.events s
        WHERE s.event_id = b.event_id
    )
    LIMIT %s;
"""

INSERT_SILVER = """
    INSERT INTO silver.events (
        event_id, event_type, 
        actor_id, actor_login, 
        repo_id, repo_name, 
        org_id, org_login, 
        event_time, is_public, payload
    )
    VALUES %s
    ON CONFLICT (event_id) DO NOTHING;
"""

# ============================================================
# Input: Only the JSON Dict
# Output: The Silver Tuple
# ============================================================
def extract_event(raw_json: dict) -> tuple | None:
    
    # A. Safety: Check the ID inside the source
    event_id = raw_json.get('id')
    if not event_id:
            #  catch the bad row here and record it in silver.log
            silver_logger.warning(f" SKIPPED: JSON missing 'id'. Data sample: {str(raw_json)[:50]}...")
            return None

    # B. Extract Objects
    actor = raw_json.get('actor') or {}
    repo = raw_json.get('repo') or {}
    org = raw_json.get('org') or {}

    # C. Time Parsing
    event_time = None
    time_str = raw_json.get('created_at')
    if time_str:
        try:
            event_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            silver_logger.debug(f"Skkipped time parsing value cannot be parssed")
            pass



    #event Logic
    event_type = str(raw_json['type']) if raw_json.get('type') else None 
    #actor logic
    actor_id = str(actor['id']) if actor.get('id') else None 
    actor_login = str(actor['login']) if actor.get('login') else None 
    # repo logic
    repo_id = str(repo['id']) if repo.get('id') else None 
    repo_name = str(repo['name']) if repo.get('name') else None 

    
    # D. Org Logic
    org_id, org_login = (None, None)
    if org:
       org_id = str(org['id']) if org.get('id') else None
       org_login = str(org['login']) if org.get('login') else None
    # E. Return Tuple
    return (
        str(event_id),                      # extracted from JSON
        event_type,               # extracted from JSON
        actor_id,
        actor_login ,
        repo_id,
        repo_name,
        org_id,
        org_login,
        event_time,
        raw_json.get('public', True),
        json.dumps(raw_json.get('payload', {}))
    )

# ============================================================
# 3. MAIN ETL LOOP
# ============================================================
def process_silver_layer():
    pipeline_logger.info(" STARTING SILVER ETL (PURE MODE)...")
    silver_logger.debug("STARTING SILVER ETL (PURE MODE)...")
    
    conn = None
    try:
        conn = psycopg2.connect(**Config.get_db_auth())
        
        while True:
            with conn.cursor() as cursor:
                cursor.execute(FETCH_UNPROCESSED, (BATCH_SIZE,))
                rows = cursor.fetchall()
                
                if not rows:
                    pipeline_logger.info(" Silver Layer is fully up to date.")
                    silver_logger.debug(" Silver Layer is fully up to date")
                    break
                
                silver_batch = []
                for row in rows:
                    # row[0] is the JSON dict because we only selected full_json
                    extracted = extract_event(row[0]) 
                    if extracted:
                        silver_batch.append(extracted)

                if silver_batch:
                    execute_values(cursor, INSERT_SILVER, silver_batch)
                    conn.commit()
                    pipeline_logger.info(f"   Saved {len(silver_batch)} events.")
                    silver_logger.info(f"   Saved {len(silver_batch)} events.")
                
    except Exception as e:
        pipeline_logger.error(f" ETL Failed: {e}")
        silver_logger.error(f" ETL Failed: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    process_silver_layer()