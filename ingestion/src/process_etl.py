import sys
import time
import signal
from datetime import timedelta , datetime
from pathlib import Path


#Path setup
current_dir=Path(__file__).resolve().parent
sys.path.append(current_dir)

#importing modules
try:
    from config import Config
    from logger import get_logger
    from process_silver import process_silver_layer
    from process_gold import process_gold_layer

except ImportError as e:
    print(f"CRITICAL ERROR MODULES FAILED TO IMPORT . {e}")
    sys.exit(1)

logger=get_logger("SILVER_GOLD_ETL_SCHEDULER" , log_filename = "Silver-gold_etl.log")


# --- GRACEFUL SHUTDOWN ---
shutdown_flag = False

def signal_handler(signum, frame):
    global shutdown_flag
    logger.warning("🛑 Shutdown signal received. Finishing current batch...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Schedule Mode

DEMO_MODE = True

# Set to True for Demo (runs every 2 mins). Set to False for Production.
if DEMO_MODE:
    POLL_INTERVAL_SECONDS = 120  # 2 minutes
    SCHEDULE_DESCRIPTION = "Every 2 minutes (Demo Mode)"
else:
    POLL_INTERVAL_SECONDS = 86400  # 24 hours
    SCHEDULE_DESCRIPTION = "Daily at 2:00 AM (Production Mode)"

# Main ETL Function

def run_etl_scheduler():
    """
    Scheduled Silver + Gold ETL
    """
    logger.info("=" * 70)
    logger.info(" SILVER + GOLD ETL SCHEDULER")
    logger.info("=" * 70)
    logger.info(f"Mode: {'DEMO' if DEMO_MODE else 'PRODUCTION'}")
    logger.info(f"Schedule: {SCHEDULE_DESCRIPTION}")
    logger.info("Layers: Bronze → Silver → Gold")
    logger.info("Bronze ingestion runs separately (main.py)")
    logger.info("Press Ctrl+C to stop gracefully")
    logger.info("=" * 70)
    
    # Validate config
    try:
        Config.validate()
        logger.info(" Configuration validated")
    except ValueError as e:
        logger.error(f" Config error: {e}")
        sys.exit(1)
    
    run_number = 0
    next_run_time = datetime.now()
    
    while not shutdown_flag:
        try:
           
            # Wait until next scheduled run
            current_time = datetime.now()
            
            if current_time < next_run_time:
                wait_seconds = (next_run_time - current_time).total_seconds()
                # Only log long waits
                if wait_seconds > 5:
                    logger.info(f" Next run: {next_run_time.strftime('%H:%M:%S')}")
                    logger.info(f" Waiting {int(wait_seconds)} seconds...")
                
                # Sleep in 1-second chunks to catch Ctrl+C
                for _ in range(int(wait_seconds)):
                    if shutdown_flag: break
                    time.sleep(1)
                
                #exit out of the main loop
                if shutdown_flag: break

            # Run ETL
            run_number +=1
            run_start = time.time()

            logger.info("")
            logger.info("="*70)
            logger.info(f" ETL RUN #{run_number} - {datetime.now().strftime('%H:%M:%S')}")
            logger.info("=" * 70)

            silver_success = False
            gold_success = False
    
            # LAYER 1: SILVER (Bronze → Silver)
            logger.info("[1/2] Silver Layer...")
            silver_start = time.time()
            
            try:
                # Call the function from process_silver.py
                process_silver_layer()
                
                silver_duration = time.time() - silver_start
                logger.info(f" Silver: Completed in {silver_duration:.2f}s")
                # The logger inside process_silver handles the details
                silver_success = True
                
            except Exception as e:
                logger.error(f" Silver failed: {e}")
                logger.warning("  Skipping Gold for this run")
            
           
            # LAYER 2: GOLD (Silver → Gold)
            
            if silver_success:
                logger.info(" [2/2] Gold Layer...")
                gold_start = time.time()
                
                try:
                    # Call the function from process_gold.py
                    process_gold_layer()
                    
                    gold_duration = time.time() - gold_start
                    logger.info(f" Gold: Completed in {gold_duration:.2f}s")
                    gold_success = True
                    
                except Exception as e:
                    logger.error(f"Gold failed: {e}")
                    logger.warning("Gold will retry next run")
            
            # Run Summary
          
            run_duration = time.time() - run_start
            
            logger.info("")
            logger.info("=" * 70)
            logger.info(f"RUN #{run_number} COMPLETE")
            logger.info(f"Silver: {'Success' if silver_success else ' Failed'}")
            logger.info(f"Gold:   {' Success' if gold_success else ' Failed'}")
            logger.info(f"Total Duration: {run_duration:.2f}s")
            logger.info("=" * 70)
            
            
            # Schedule Next Run
           
            if DEMO_MODE:
                # Demo: Run every 2 minutes from now
                next_run_time = datetime.now() + timedelta(seconds=POLL_INTERVAL_SECONDS)
            else:
                # Production: Next day at 2:00 AM
                next_run_time = datetime.now() + timedelta(days=1)
                next_run_time = next_run_time.replace(hour=2, minute=0, second=0, microsecond=0)
                
                # If already past 2 AM today, schedule for tomorrow
                if next_run_time <= datetime.now():
                    next_run_time += timedelta(days=1)
            
        except KeyboardInterrupt:
            logger.warning(" Keyboard interrupt detected")
            break
            
        except Exception as e:
            logger.error(f" Critical error in run #{run_number}: {e}")
            logger.info("  Retrying in 1 minute...")
            time.sleep(60)
            next_run_time = datetime.now() + timedelta(minutes=1)
    
    # Graceful shutdown
    logger.info("=" * 70)
    logger.info(" ETL SCHEDULER STOPPED")
    logger.info(f"Total runs: {run_number}")
    logger.info("=" * 70)

if __name__ == "__main__":
    run_etl_scheduler()