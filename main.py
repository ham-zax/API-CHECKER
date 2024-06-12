import requests
import time
import signal
import sys
import random
from tabulate import tabulate  # Import tabulate module
from config import API_URL, PARAMS, INTERVAL
from utils import process_response, handle_error, notify_new_3995

# To track seen hostnodes with '3995' CPU type
seen_hostnodes = set()

def fetch_api_data():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_error(e)
        return None  # Return None in case of an error

def main():
    def signal_handler(sig, frame):
        print("Stopping the script...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print("Running the script. Press Ctrl+C to stop.")

    while True:
        print("Checking for new hostnodes...")
        data = fetch_api_data()
        if data:
            new_3995_nodes, current_3995_nodes = process_response(data, seen_hostnodes)
            if new_3995_nodes:
                notify_new_3995(new_3995_nodes)

            # Display current 3995 nodes in the console
            if current_3995_nodes:
                table = tabulate(current_3995_nodes, headers="keys")
                print(table)
        
        # Calculate the next sleep interval randomly within the specified range
        sleep_interval = random.randint(int(INTERVAL * 0.8), int(INTERVAL * 1.2))
        print(f"Sleeping for {sleep_interval} seconds...")
        time.sleep(sleep_interval)

if __name__ == "__main__":
    main()
