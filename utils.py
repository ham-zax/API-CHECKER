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
        return False
    return True

def parse_gpu_types(gpu_types):
    gpu_multipliers = {}
    for entry in gpu_types:
        try:
            gpu, multiplier = entry.split(",")
            gpu_multipliers[gpu.strip().lower()] = float(multiplier)
        except ValueError:
            logging.error(f"Invalid GPU entry: {entry}")
    return gpu_multipliers

def get_multiplier(gpu_type, gpu_multipliers):
    for gpu, multiplier in gpu_multipliers.items():
        if gpu in gpu_type.lower():
            return multiplier
    return None

def process_response(data, seen_hostnodes):
    new_cpu_nodes = []
    new_gpu_nodes = []
    current_cpu_nodes = []
    current_gpu_nodes = []

    gpu_multipliers = parse_gpu_types(GPU_TYPES)
    telegram_failed = False

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
                        f"*CPU:* {cpu_info['type']}\n"
                        f"*Amount:* {cpu_info['amount']}\n"
                        f"*Price:* {cpu_info['price']}\n"
                        f"*Status:* {'Online' if hostnode['status']['online'] else 'Offline'}\n"
                        f"{'='*40}"
                    )
                    if len(message) > 4096:
                        message = message[:4093] + "..."
                    if not send_telegram_message(message):
                        telegram_failed = True
                    print(message)

            gpu_info = hostnode['specs']['gpu']
            for gpu_type, gpu_specs in gpu_info.items():
                if any(gpu in gpu_type.lower() for gpu in gpu_multipliers) and (MAX_GPU_PRICE == 0 or gpu_specs['price'] <= MAX_GPU_PRICE):
                    amount = gpu_specs['amount'] if gpu_specs['amount'] > 0 else 1  # If amount is 0, assume 1 GPU
                    price = gpu_specs['price']
                    multiplier = get_multiplier(gpu_type, gpu_multipliers)
                    if multiplier is not None:
                        total_multiplier = multiplier * amount
                        efficiency = round(total_multiplier / price, 2) if price > 0 else 0
                        cost_per_device = price / amount if amount > 0 else price
                        calculation = f"({multiplier} x {amount}) / {price}"
                    else:
                        efficiency = "N/A"
                        cost_per_device = price / amount if amount > 0 else price
                        calculation = "N/A"

                    current_gpu_nodes.append({
                        'id': key,
                        'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                        'gpu': gpu_type,
                        'amount': gpu_specs['amount'],
                        'price': price,
                        'status': 'Online' if hostnode['status']['online'] else 'Offline',
                        'cost_per_device': cost_per_device,
                        'multiplier': multiplier if multiplier else "N/A",
                        'efficiency': efficiency,
                        'calculation': calculation
                    })
                    if key not in seen_hostnodes:
                        seen_hostnodes.add(key)
                        new_gpu_nodes.append({**hostnode, 'id': key})
                        message = (
                            f"*Hostnode ID:* `{key}`\n"
                            f"*GPU:* {gpu_type}\n"
                            f"*Amount:* {gpu_specs['amount']}\n"
                            f"*Price:* {price}\n"
                            f"*Cost per device:* {cost_per_device}\n"
                            f"*Multiplier:* {multiplier if multiplier else 'N/A'}\n"
                            f"*Efficiency:* {efficiency}\n"
                            f"*Calculation:* {calculation}\n"
                            f"*Status:* {'Online' if hostnode['status']['online'] else 'Offline'}\n"
                            f"{'='*40}"
                        )
                        if len(message) > 4096:
                            message = message[:4093] + "..."
                        if not send_telegram_message(message):
                            telegram_failed = True
                        print(message)
    else:
        logging.error("API request was not successful")

    if telegram_failed:
        logging.error("Failed to send some Telegram notifications")

    return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes

def handle_error(error):
    logging.error(f"An error occurred: {error}")

def notify_new_cpu_nodes(new_cpu_nodes):
    logging.info(f"Found {len(new_cpu_nodes)} new hostnodes with {CPU_TYPE} CPU:")
    for node in new_cpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")

def notify_new_gpu_nodes(new_gpu_nodes):
    logging.info(f"Found {len(new_gpu_nodes)} new hostnodes with GPUs up to price {MAX_GPU_PRICE}:")
    for node in new_gpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")
