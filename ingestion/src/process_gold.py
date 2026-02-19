import sys
import psycopg2
from pathlib import Path

# ==========================================
# 1. Path Setup (Dynamic & Robust)
# ==========================================
# Get the directory where this script lives (ingestion/src)
current_dir = Path(__file__).resolve().parent

# Add 'ingestion/src' to Python path so we can import local modules
sys.path.append(str(current_dir))

# Add project root for finding SQL files
project_root = current_dir.parent.parent

# ==========================================
# 2. Local Module Imports
# ==========================================
try:
    from config import Config
    from logger import get_logger
except ImportError as e:
    print(f" CRITICAL ERROR: Could not import project modules. {e}")
    sys.exit(1)

# Initialize Logger
logger = get_logger("GOLD_ETL")

def process_gold_layer():
    """
    Orchestrates the Gold ETL transaction.
    - Connects with Autocommit OFF
    - Runs the Master SQL Script
    - Captures DB logs (RAISE NOTICE)
    - Commits on success / Rolls back on failure
    """
    conn = None
    cursor = None
    
    # Path to your Master SQL File
    sql_file_path = project_root / 'warehouse' / 'gold' / 'etl' / 'master_gold_etl.sql'

    try:
        logger.info("=" * 60)
        logger.info(" STARTING GOLD LAYER ETL")
        logger.info(f" Script: {sql_file_path.name}")
        logger.info("=" * 60)

        # Step 1: Connect to DB
     
        db_params = Config.get_db_auth()
        conn = psycopg2.connect(**db_params)
        

        # If one step fails, undo EVERYTHING.
        conn.autocommit = False 
        cursor = conn.cursor()


        #  Read & Execute SQL

        if not sql_file_path.exists():
            raise FileNotFoundError(f"SQL file not found at: {sql_file_path}")

        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        logger.info("Executing Transactional SQL...")
        cursor.execute(sql_script)

        #  Capture & Log DB Output

        if conn.notices:
            logger.info("---  DATABASE LOGS ---")
            for notice in conn.notices:
                clean_msg = notice.strip().replace("NOTICE:  ", "")
                if clean_msg:
                    logger.info(f"   {clean_msg}")
            logger.info("------------------------")

        # Commit Transaction

        conn.commit()
        logger.info("COMMIT SUCCESSFUL: Gold Layer is up to date.")

    except psycopg2.Error as db_err:

        # Step 5: Handle DB Failures

        logger.error(f"DATABASE ERROR: {db_err}")
        if conn:
            conn.rollback()
            logger.warning(" TRANSACTION ROLLED BACK. No changes saved.")
        raise db_err
        

    except Exception as e:
        #  Handle System Failures
   
        logger.error(f" SYSTEM ERROR: {e}")
        if conn:
            conn.rollback()
        raise e
    

    finally:
   
        if cursor: cursor.close()
        if conn: conn.close()
        logger.info(" Database connection closed.")

if __name__ == "__main__":
    process_gold_layer()