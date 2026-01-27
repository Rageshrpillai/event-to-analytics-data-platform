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

    try:
        # 3. Connect using Context Manager
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                logger.info("🔌 Connected to Database...")

                # 4. Read and Execute Bronze DDL
                file_path = "warehouse/bronze/ddl.sql"
                logger.info(f" Executing: {file_path}")
                
                with open(file_path, "r") as f:
                    sql_script = f.read()
                    cursor.execute(sql_script)
                
                logger.info(" Bronze Layer Created Successfully!")
                
        
    except Exception as e:
        logger.error(f" Setup Failed: {e}")

if __name__ == "__main__":
    setup_database()