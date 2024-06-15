import requests
import logging
from tabulate import tabulate
from config import TELEGRAM_TOKEN, CHAT_ID, CPU_TYPE, GPU_TYPES, MAX_GPU_PRICE
import matplotlib.pyplot as plt
from PIL import Image
import io
from typing import List, Dict, Tuple, Union, Optional, Any

logging.basicConfig(level=logging.INFO)

def send_telegram_message(photo: io.BytesIO) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data = {'chat_id': CHAT_ID}
    try:
        files = {'photo': photo}
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False
    return True

def parse_gpu_types(gpu_types: List[str]) -> Dict[str, Optional[float]]:
    gpu_multipliers = {}
    for entry in gpu_types:
        parts = entry.split(",")
        if len(parts) == 2:
            gpu, multiplier = parts
            gpu_multipliers[gpu.strip().lower()] = float(multiplier)
        elif len(parts) == 1:
            gpu = parts[0]
            gpu_multipliers[gpu.strip().lower()] = None
        else:
            logging.error(f"Invalid GPU entry: {entry}")
    return gpu_multipliers

def get_multiplier(gpu_type: str, gpu_multipliers: Dict[str, Optional[float]]) -> Optional[float]:
    for gpu, multiplier in gpu_multipliers.items():
        if gpu in gpu_type.lower():
            return multiplier
    return None

def shorten_id(node_id: str) -> str:
    return f"{node_id[:2]}..{node_id[-2:]}"

def generate_table_image(data: List[List[Any]], headers: List[str]) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(15, len(data) * 0.5))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=data, colLabels=headers, cellLoc='center', loc='center')

    col_widths = [0.08, 0.35, 0.1, 0.1, 0.1, 0.1, 0.1, 0.17]
    for i, width in enumerate(col_widths):
        for j in range(len(data) + 1):
            cell = table[j, i]
            cell.set_width(width)
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return buf

def process_response(data: Dict[str, Any], seen_hostnodes: set) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
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
                if key not in seen_hostnodes:
                    seen_hostnodes.add(key)
                    new_cpu_nodes.append({**hostnode, 'id': key})
                current_cpu_nodes.append({
                    'id': key,
                    'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                    'cpu': cpu_info['type'],
                    'amount': cpu_info['amount'],
                    'price': f"${cpu_info['price']:.2f}",
                    'status': 'Online' if hostnode['status']['online'] else 'Offline'
                })

            gpu_info = hostnode['specs']['gpu']
            for gpu_type, gpu_specs in gpu_info.items():
                if gpu_specs['amount'] > 0 and (any(gpu in gpu_type.lower() for gpu in gpu_multipliers) and (MAX_GPU_PRICE == 0 or gpu_specs['price'] <= MAX_GPU_PRICE)):
                    amount = gpu_specs['amount']
                    price_per_unit = gpu_specs['price']
                    total_price = price_per_unit * amount
                    multiplier = get_multiplier(gpu_type, gpu_multipliers)
                    cost_per_device = price_per_unit

                    if key not in seen_hostnodes:
                        seen_hostnodes.add(key)
                        new_gpu_nodes.append({**hostnode, 'id': key})

                    current_gpu_nodes.append({
                        'id': key,
                        'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                        'gpu': gpu_type,
                        'amount': amount,
                        'price': f"${total_price:.2f}",
                        'status': 'Online' if hostnode['status']['online'] else 'Offline',
                        'cost_per_device': f"${cost_per_device:.2f}",
                        'multiplier': multiplier if multiplier else "N/A",
                        'efficiency': None if multiplier is None else round((multiplier * amount) / total_price, 2),
                        'calculation': None if multiplier is None else f"({multiplier:.2f} x {amount}) / {total_price:.2f}"
                    })

    else:
        logging.error("API request was not successful")

    combined_data = []
    for node in current_cpu_nodes:
        combined_data.append([
            shorten_id(node['id']),
            node['cpu'],
            node['amount'],
            node['price'],
            '-', '-', '-', '-'
        ])

    for node in current_gpu_nodes:
        combined_data.append([
            shorten_id(node['id']),
            node['gpu'],
            node['amount'],
            node['price'],
            node['cost_per_device'],
            node['multiplier'],
            node['efficiency'],
            node['calculation']
        ])

    headers = ["ID", "Type", "Amount", "Price ($)", "Cost per Device ($)", "Multiplier", "Efficiency", "Calculation"]
    table_image = generate_table_image(combined_data, headers)

    if not send_telegram_message(table_image):
        logging.error("Failed to send some Telegram notifications")

    print(tabulate(combined_data, headers=headers))

    return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes

def handle_error(error: Exception) -> None:
    logging.error(f"An error occurred: {error}")

def notify_new_cpu_nodes(new_cpu_nodes: List[Dict[str, Any]]) -> None:
    logging.info(f"Found {len(new_cpu_nodes)} new hostnodes with {CPU_TYPE} CPU:")
    for node in new_cpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")

def notify_new_gpu_nodes(new_gpu_nodes: List[Dict[str, Any]]) -> None:
    logging.info(f"Found {len(new_gpu_nodes)} new hostnodes with GPUs up to price {MAX_GPU_PRICE}:")
    for node in new_gpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        logging.info(f"Hostnode ID: {node_id}")

