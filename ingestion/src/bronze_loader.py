import sys
import json
import psycopg2
from pathlib import Path
from typing import List, Dict, Any

# --- PATH SETUP ---
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from config import Config
from logger import get_logger

logger = get_logger("BRONZE_LOADER", log_filename="bronze.log")

def load_to_bronze(events: List[Dict[str, Any]]):
    """
    Inserts raw events into the Bronze layer.
    Handles duplicates via 'ON CONFLICT DO NOTHING'.
    """
    if not events:
        logger.info(" No events to load.")
        return

    # 1. The Insert Query
    # We dump the whole JSON object into 'full_json'
    insert_query = """
    INSERT INTO bronze.raw_events (event_id, event_type, full_json)
    VALUES (%s, %s, %s)
    ON CONFLICT (event_id) DO NOTHING;
    """

    # 2. The Dead Letter Queue Query
    # If a specific row is bad, we save it here instead of crashing
    dlq_query = """
    INSERT INTO bronze.dead_letter_queue (failed_payload, error_message)
    VALUES (%s, %s);
    """

    conn = None
    try:
        # Connect to DB using our secure Config
        with psycopg2.connect(**Config.get_db_auth()) as conn:
            with conn.cursor() as cursor:
                
                success_count = 0
                duplicate_count = 0
                error_count = 0

                for event in events:
                    try:
                        # Extract basic info
                        e_id = event.get("id")
                        e_type = event.get("type")
                        e_json = json.dumps(event) 

                        # Execute the safe insert
                        cursor.execute(insert_query, (e_id, e_type, e_json))
                        
                       
                        if cursor.rowcount == 0:
                            duplicate_count += 1
                        else:
                            success_count += 1

                    except Exception as row_error:
                        # --- ROW LEVEL ERROR HANDLING ---
                        conn.rollback() # Undo ONLY this failed row
                        error_count += 1
                        logger.error(f"Row Error: {row_error}")
                        
                        # Send to DLQ
                        try:
                            cursor.execute(dlq_query, (json.dumps(event), str(row_error)))
                            conn.commit()
                        except Exception as e:
                           logger.critical(f"DLQ Failed: {e}")

                # Commit the batch of successful inserts
                conn.commit()
                logger.info(f" Batch Report: {success_count} Inserted | {duplicate_count} Duplicates | {error_count} Errors")

    except Exception as e:
        logger.error(f" Critical Database Connection Error: {e}")
        raise e
    finally:
        if conn: conn.close()

# --- INTEGRATION TEST BLOCK ---
if __name__ == "__main__":
    # When you run this file directly, it will import the API client
    from api_client import fetch_events
    
    print("--- STARTING INTEGRATION TEST ---")
    
    # 1. Get Data from GitHub
    raw_data = fetch_events()
    
    # 2. Load Data to Postgres
    load_to_bronze(raw_data)
    
    print("--- END INTEGRATION TEST ---")