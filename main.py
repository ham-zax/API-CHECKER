import requests
import time
import signal
import sys
import random
import logging
from tabulate import tabulate
from config import API_URL, PARAMS, INTERVAL
from utils import process_response, handle_error, notify_new_cpu_nodes, notify_new_gpu_nodes

logging.basicConfig(level=logging.INFO)

seen_hostnodes = set()

def fetch_api_data():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_error(e)
        return None

def main():
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

            # Display current CPU nodes in the console
            if current_cpu_nodes:
                table = tabulate(current_cpu_nodes, headers="keys")
                logging.info(f"\n{table}")

            # Display current GPU nodes in the console
            if current_gpu_nodes:
                table = tabulate(current_gpu_nodes, headers="keys")
                logging.info(f"\n{table}")
        
        # Calculate the next sleep interval randomly within the specified range
        sleep_interval = random.randint(int(INTERVAL * 0.8), int(INTERVAL * 1.2))
        logging.info(f"Sleeping for {sleep_interval} seconds...")
        time.sleep(sleep_interval)

if __name__ == "__main__":
    main()
