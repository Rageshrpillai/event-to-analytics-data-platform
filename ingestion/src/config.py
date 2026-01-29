import os
import sys
from dotenv import load_dotenv
from typing import Dict

#load env variables to system
load_dotenv(verbose=True)

# GROUPING  FUNCTIONS AND VARIABLE INTO ONE CLASS LIKE A FOLDER STRUCTURE
class Config:
    """
    Central configuration handling.
    Raises errors immediately if critical secrets are missing.
    """
    
    # Database Config with Type Hints
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "github_events")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS") 
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    # API Config
    GITHUB_URL: str = "https://api.github.com/events"
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN") # EXPECT KEY OR NONE

    @classmethod #USING CLASS DECORATOR FOR SPECIFYING WE USE CLASS VERIABLES AS INPUTS
    def validate(cls):
        """
        Checks for required environment variables.
        Exits the program if critical config is missing.
        """
        missing_keys = []
        
        if not cls.DB_PASS: missing_keys.append("DB_PASS")
        if not cls.DB_USER: missing_keys.append("DB_USER")
        
        # If any keys are missing, crash intentionally
        if missing_keys:
            error_msg = f" CRITICAL ERROR: Missing environment variables: {', '.join(missing_keys)}"
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)

    @staticmethod
    def get_db_auth() -> Dict[str, str]:
        """Helper to get DB connection details as a dictionary"""
        # Ensure config is valid before returning credentials
        Config.validate()
        
        return {
            "host": Config.DB_HOST,
            "database": Config.DB_NAME,
            "user": Config.DB_USER,
            "password": Config.DB_PASS,
            "port": Config.DB_PORT
        }

# --- TEST BLOCK (Run this file to check your .env) ---
if __name__ == "__main__":
    try:
        Config.validate()
        print("✅ Configuration is valid.")
        print(f"🔌 DB Host: {Config.DB_HOST}")
        print(f"👤 DB User: {Config.DB_USER}")
        # Securely check token presence
        token_status = "Yes" if Config.GITHUB_TOKEN else "No (Rate Limit: 60/hr)"
        print(f"🔑 Token Present: {token_status}")
    except ValueError as e:
        print("🛑 Configuration failed.")