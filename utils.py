
# api_checker/utils.py
def process_response(data):
    if data.get("success"):
        hostnodes = data.get("hostnodes", {})
        for key, hostnode in hostnodes.items():
            print(f"Hostnode ID: {key}")
            print(f"Location: {hostnode['location']['city']}, {hostnode['location']['country']}")
            print(f"Status: {'Online' if hostnode['status']['online'] else 'Offline'}")
            print("="*40)
    else:
        print("API request was not successful")

def handle_error(error):
    print(f"An error occurred: {error}")
