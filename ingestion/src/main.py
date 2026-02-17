import sys
import time
import signal
from pathlib import Path

# --- PATH SETUP ---
# Add 'src' to path so we can import modules
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from config import Config
from logger import get_logger
from api_client import fetch_events
# Import your specific loader function
from bronze_loader import load_to_bronze 

# Initialize Logger
logger = get_logger("ORCHESTRATOR")

# --- GRACEFUL SHUTDOWN ---
# This ensures that if you press Ctrl+C, the program stops safely
shutdown_flag = False

def signal_handler(signum, frame):
    global shutdown_flag
    logger.info(" Shutdown signal received. Finishing current batch...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_pipeline():
    """
    The main infinite loop that keeps the pipeline running.
    """
    logger.info(" Pipeline started. Press Ctrl+C to stop.")
    
    # Validate Config once at startup
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    while not shutdown_flag:
        try:
            start_time = time.time()
            
        
            # The API Client fetches data
            events = fetch_events()
            
            
            # The Loader puts it into Postgres
            if events:
                load_to_bronze(events)
            
            
            #  run every 60 seconds roughly
            elapsed = time.time() - start_time
            sleep_time = max(10, 60 - elapsed)
            
            logger.info(f" Sleeping for {int(sleep_time)} seconds...")
            
            # Sleep in short bursts so it  can catch Ctrl+C faster
            for _ in range(int(sleep_time)):
                if shutdown_flag: break
                time.sleep(1)

        except Exception as e:
            logger.error(f" Unexpected Error in Main Loop: {e}")
            logger.info(" Retrying in 60 seconds...")
            time.sleep(60)

    logger.info(" Pipeline stopped gracefully.")

if __name__ == "__main__":
    run_pipeline()