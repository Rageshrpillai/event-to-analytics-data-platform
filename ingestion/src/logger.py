import logging
import sys
from pathlib import Path
from typing import Optional

# --- LOGGING CONFIG ---
# This ensures logs are saved relative to this file
# Result: ingestion/logs/pipeline.log
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "pipeline.log"

# Ensure the logs directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates a standardized logger that writes to both Console and File.
    
    Args:
        name (str): The name of the module.
        level (int): Logging level (default: logging.INFO).
    """
    logger = logging.getLogger(name)
    
    # Singleton check: If handlers exist, don't add them again
    if not logger.handlers:
        logger.setLevel(level)
        
        # Format: 2026-01-29 10:00:00 - MODULE - INFO - Message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console Handler (For Terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler (For Permanent Records)
        # mode='a' means "Append" (don't delete old logs)
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# --- TEST BLOCK ---
if __name__ == "__main__":
    print(f"📁 Log file location: {LOG_FILE}")
    
    test_logger = get_logger("TEST_MONITOR")
    test_logger.info("✅ This message goes to Console AND File")
    test_logger.error("❌ This error is permanently recorded in pipeline.log")