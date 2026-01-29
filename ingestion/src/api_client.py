import sys
import requests
from pathlib import Path
from typing import List, Dict, Any

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from config import Config
from logger import get_logger

# Initialize Logger
logger = get_logger("API_CLIENT")

def fetch_events() -> List[Dict[str, Any]]:
    """
    Fetches the latest public events from GitHub.
    
    Returns:
        List[Dict]: A list of dictionary objects containing event data.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "python-data-pipeline-v1",
    }

    # Add Token if it exists
    if Config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {Config.GITHUB_TOKEN}"

    try:
        # Fetch up to 100 events
        params = {"per_page": 100}
        
        logger.info(f"Fetching events from {Config.GITHUB_URL}...")
        response = requests.get(
            Config.GITHUB_URL, 
            headers=headers, 
            params=params, 
            timeout=10
        )
        
        # We check the headers to see what our limit is
        rate_limit = response.headers.get("X-RateLimit-Limit")
        rate_remaining = response.headers.get("X-RateLimit-Remaining")
        
        if rate_limit:
            if int(rate_limit) == 60:
                logger.warning(f" Unauthenticated! Limit: {rate_limit} (Remaining: {rate_remaining})")
            elif int(rate_limit) > 60:
                logger.info(f" Authenticated! Limit: {rate_limit} (Remaining: {rate_remaining})")
            else:
                logger.info(f" Rate Limit: {rate_limit}")


        # Raise error for 4xx or 5xx status codes
        response.raise_for_status()
        
        data = response.json()

        logger.info(f" Successfully fetched {len(data)} events.")
        return data

    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            logger.error(" Rate Limit Exceeded! Check your GITHUB_TOKEN.")
        else:
            logger.error(f" HTTP Error: {e}")
        return []
        
    except Exception as e:
        logger.error(f" Connection Failed: {e}")
        return []

# --- TEST BLOCK ---
# Run directly: python ingestion/src/api_client.py
if __name__ == "__main__":
    print("--- STARTING TEST ---")
    events = fetch_events()
    if events:
        # Using .get() is safer than direct access in case keys are missing
        first_event = events[0]
        print(f"Sample Event ID: {first_event.get('id')}")
        print(f"Sample Type:     {first_event.get('type')}")
        
        # Handle nested keys safely
        actor = first_event.get('actor', {})
        print(f"Sample Actor:    {actor.get('login')}")
    else:
        print("No events fetched.")
    print("--- END TEST ---")