# api_checker/main.py
import requests
import time
import signal
import sys
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

def main():
    def signal_handler(sig, frame):
        print("Stopping the script...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print("Running the script. Press Ctrl+C to stop.")

    while True:
        data = fetch_api_data()
        if data:
            new_3995_nodes = process_response(data, seen_hostnodes)
            if new_3995_nodes:
                notify_new_3995(new_3995_nodes)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
