from typing import List, Dict, Any
import requests
import logging
from config import config
import io

# Create a custom filter
class HostnodeIDFilter(logging.Filter):
    def filter(self, record):
        return "Hostnode ID:" not in record.getMessage()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
# Add the custom filter to the logger
logger.addFilter(HostnodeIDFilter())

def send_telegram_message(photo: io.BytesIO) -> bool:
    """Send a photo to a Telegram chat using the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendPhoto"
    data = {'chat_id': config.CHAT_ID}
    try:
        files = {'photo': photo}
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False
    return True

def notify_new_cpu_nodes(new_cpu_nodes: List[Dict[str, Any]]) -> None:
    """Log information about new CPU nodes."""
    logging.info(f"Found {len(new_cpu_nodes)} new hostnodes with {config.CPU_TYPE} CPU:")
    for node in new_cpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")

def notify_new_gpu_nodes(new_gpu_nodes: List[Dict[str, Any]]) -> None:
    """Log information about new GPU nodes."""
    logging.info(f"Found {len(new_gpu_nodes)} new hostnodes with GPUs up to price {config.MAX_GPU_PRICE}:")
    for node in new_gpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")
