import requests
import logging
from tabulate import tabulate
from config import TELEGRAM_TOKEN, CHAT_ID, CPU_TYPE, GPU_TYPES, MAX_GPU_PRICE

logging.basicConfig(level=logging.INFO)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")

def process_response(data, seen_hostnodes):
    new_cpu_nodes = []
    new_gpu_nodes = []
    current_cpu_nodes = []
    current_gpu_nodes = []

    if data.get("success"):
        hostnodes = data.get("hostnodes", {})
        for key, hostnode in hostnodes.items():
            cpu_info = hostnode['specs']['cpu']
            if CPU_TYPE in cpu_info['type']:
                current_cpu_nodes.append({
                    'id': key,
                    'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                    'cpu': cpu_info['type'],
                    'amount': cpu_info['amount'],
                    'price': cpu_info['price'],
                    'status': 'Online' if hostnode['status']['online'] else 'Offline'
                })
                if key not in seen_hostnodes:
                    seen_hostnodes.add(key)
                    new_cpu_nodes.append({**hostnode, 'id': key})
                    message = (
                        f"*Hostnode ID:* `{key}`\n"
                        f"*Location:* {hostnode['location']['city']}, {hostnode['location']['country']}\n"
                        f"*CPU:* {cpu_info['type']} - *Amount:* {cpu_info['amount']} - *Price:* {cpu_info['price']}\n"
                        f"*Status:* {'Online' if hostnode['status']['online'] else 'Offline'}\n"
                        f"{'='*40}"
                    )
                    if len(message) > 4096:
                        message = message[:4093] + "..."
                    send_telegram_message(message)

            gpu_info = hostnode['specs']['gpu']
            for gpu_type, gpu_specs in gpu_info.items():
                if (not GPU_TYPES or any(gpu in gpu_type for gpu in GPU_TYPES)) and (MAX_GPU_PRICE == 0 or gpu_specs['price'] <= MAX_GPU_PRICE):
                    cost_per_device = gpu_specs['price'] / gpu_specs['amount'] if gpu_specs['amount'] > 1 else gpu_specs['price']
                    current_gpu_nodes.append({
                        'id': key,
                        'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                        'gpu': gpu_type,
                        'amount': gpu_specs['amount'],
                        'price': gpu_specs['price'],
                        'status': 'Online' if hostnode['status']['online'] else 'Offline',
                        'cost_per_device': cost_per_device
                    })
                    if key not in seen_hostnodes:
                        seen_hostnodes.add(key)
                        new_gpu_nodes.append({**hostnode, 'id': key})
                        message = (
                            f"*Hostnode ID:* `{key}`\n"
                            f"*Location:* {hostnode['location']['city']}, {hostnode['location']['country']}\n"
                            f"*GPU:* {gpu_type}\n"
                            f"*Amount:* {gpu_specs['amount']}\n"
                            f"*Price:* {gpu_specs['price']}\n"
                            f"*Cost per device:* {cost_per_device}\n"
                            f"*Status:* {'Online' if hostnode['status']['online'] else 'Offline'}\n"
                            f"{'='*40}"
                        )
                        if len(message) > 4096:
                            message = message[:4093] + "..."
                        send_telegram_message(message)
    else:
        logging.error("API request was not successful")
    
    return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes

def handle_error(error):
    logging.error(f"An error occurred: {error}")

def notify_new_cpu_nodes(new_cpu_nodes):
    logging.info(f"Found {len(new_cpu_nodes)} new hostnodes with {CPU_TYPE} CPU:")
    for node in new_cpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")

def notify_new_gpu_nodes(new_gpu_nodes):
    logging.info(f"Found {len(new_gpu_nodes)} new hostnodes with GPUs {GPU_TYPES} up to price {MAX_GPU_PRICE}:")
    for node in new_gpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")
