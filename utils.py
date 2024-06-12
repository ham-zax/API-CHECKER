# api_checker/utils.py
def process_response(data, seen_hostnodes):
    new_3995_nodes = []
    if data.get("success"):
        hostnodes = data.get("hostnodes", {})
        for key, hostnode in hostnodes.items():
            cpu_info = hostnode['specs']['cpu']
            if "3995" in cpu_info['type']:
                if key not in seen_hostnodes:
                    seen_hostnodes.add(key)
                    new_3995_nodes.append(hostnode)
                print(f"Hostnode ID: {key}")
                print(f"Location: {hostnode['location']['city']}, {hostnode['location']['country']}")
                print(f"CPU: {cpu_info['type']} - Amount: {cpu_info['amount']} - Price: {cpu_info['price']}")
                print(f"Status: {'Online' if hostnode['status']['online'] else 'Offline'}")
                print("="*40)
    else:
        print("API request was not successful")
    return new_3995_nodes

def handle_error(error):
    print(f"An error occurred: {error}")

def notify_new_3995(new_3995_nodes):
    print(f"Found {len(new_3995_nodes)} new hostnodes with 3995 CPU:")
    for node in new_3995_nodes:
        print(f"Hostnode ID: {node['id']}")
