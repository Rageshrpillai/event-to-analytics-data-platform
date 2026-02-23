import psycopg2
import os
import logging
import sys
from dotenv import load_dotenv


# 1. Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DB_SETUP")

# 2. Load Environment Variables
load_dotenv()

def setup_database():
    # Database Config Dictionary
    db_config = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "port": os.getenv("DB_PORT")
    }

    if not all(db_config.values()):
        raise ValueError("Missing DB environment variables")
    sql_files = [
            "warehouse/bronze/ddl.sql",
            "warehouse/silver/ddl.sql",
            "warehouse/silver/view_silver.sql",
            "warehouse/gold/01_dim_date.sql",
            "warehouse/gold/02_dim_actors.sql",
            "warehouse/gold/03_dim_repos.sql",
            "warehouse/gold/04_dim_event_types.sql",
            "warehouse/gold/05_fact_events.sql",
        ]

    try:
            with psycopg2.connect(**db_config) as conn:
                with conn.cursor() as cursor:
                    for file_path in sql_files:
                        logger.info(f"Executing: {file_path}")
                        with open(file_path, "r") as f:
                            cursor.execute(f.read())
                        logger.info(f" Done: {file_path}")
                        
            logger.info(" Full database setup complete!")
            
    except Exception as e:
            logger.error(f"Setup Failed: {e}")

if __name__ == "__main__":
    setup_database()