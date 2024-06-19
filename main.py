import time
import signal
import sys
import random
import logging
from api_fetcher import fetch_api_data
from processor import process_response
from notifier import notify_new_cpu_nodes, notify_new_gpu_nodes
from config import config

logging.basicConfig(level=logging.INFO)

seen_hostnodes = set()

def main():
    """Main script to fetch API data, process it, and notify about new nodes."""
    def signal_handler(sig, frame):
        logging.info("Stopping the script...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    logging.info("Running the script. Press Ctrl+C to stop.")

    while True:
        logging.info("Checking for new hostnodes...")
        data = fetch_api_data()
        if data:
            new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes = process_response(data, seen_hostnodes)
            if new_cpu_nodes:
                notify_new_cpu_nodes(new_cpu_nodes)
            if new_gpu_nodes:
                notify_new_gpu_nodes(new_gpu_nodes)

        sleep_interval = random.randint(int(config.INTERVAL * 0.8), int(config.INTERVAL * 1.2))
        logging.info(f"Sleeping for {sleep_interval} seconds...")
        time.sleep(sleep_interval)

if __name__ == "__main__":
    main()
