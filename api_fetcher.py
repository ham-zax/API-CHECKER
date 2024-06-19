from typing import Any, Dict, Optional
import requests
from config import config
import logging

logging.basicConfig(level=logging.INFO)

def fetch_api_data() -> Optional[Dict[str, Any]]:
    """Fetch data from the API and handle any errors."""
    try:
        response = requests.get(config.API_URL, params=config.PARAMS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch API data: {e}")
        return None
