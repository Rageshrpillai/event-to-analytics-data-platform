import logging
import sys
from pathlib import Path
from typing import Optional

# --- LOGGING CONFIG ---
# Define the base log directory: ingestion/logs/
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

# Ensure the logs directory exists immediately
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: str, level: int = logging.INFO, log_filename: str = "pipeline.log") -> logging.Logger:
    """
    Creates a standardized logger that writes to Console AND a specific File.
    
    Args:
        name (str): The name of the module (e.g., "SILVER_PROCESSOR").
        level (int): Logging level (default: logging.INFO).
        log_filename (str): The specific log file to write to. 
                            Defaults to "pipeline.log" if not provided.
    """
    logger = logging.getLogger(name)
    
    # Singleton check: Only set up handlers if they don't exist yet
    if not logger.handlers:
        logger.setLevel(level)
        
        # Format: 2026-02-05 10:00:00 - MODULE - INFO - Message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console Handler (Standard Output)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler (Dynamic File)
        # We construct the full path using the requested filename
        target_log_file = LOG_DIR / log_filename
        
        # mode='a' means "Append" (keep history)
        file_handler = logging.FileHandler(target_log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# --- TEST BLOCK ---
if __name__ == "__main__":
    print(f"📁 Log directory: {LOG_DIR}")
    
    # Test 1: Default (goes to pipeline.log)
    default_logger = get_logger("TEST_DEFAULT")
    default_logger.info("✅ This goes to the default 'pipeline.log'")
    
    # Test 2: Custom (goes to separate file)
    silver_logger = get_logger("SILVER_TEST", log_filename="silver_layer.log")
    silver_logger.warning("⚠️ This specific warning goes to 'silver_layer.log'")
    
    print("✅ Test complete. Check the 'logs' folder.")