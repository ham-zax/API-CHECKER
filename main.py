
# api_checker/main.py
import requests
from config import API_URL, PARAMS
from utils import process_response, handle_error

def fetch_api_data():
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_error(e)

def main():
    data = fetch_api_data()
    if data:
        process_response(data)

if __name__ == "__main__":
    main()
