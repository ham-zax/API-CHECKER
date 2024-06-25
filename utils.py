# notification.py
import requests
import logging
from tabulate import tabulate
from config import TELEGRAM_TOKEN, CHAT_IDS, CPU_TYPE, GPU_TYPES, MAX_GPU_PRICE, MIN_EFFICIENCY, ENABLE_CPU
import matplotlib.pyplot as plt
from PIL import Image
import io
from typing import List, Dict, Tuple, Optional, Any

logging.basicConfig(level=logging.INFO)

def send_telegram_message(photo: io.BytesIO) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    success = True
    for chat_id in CHAT_IDS:
        logging.info(f"Sending message to chat ID: {chat_id}")
        data = {'chat_id': chat_id}
        try:
            # Check if the photo data is empty
            photo.seek(0, 2)  # Seek to the end of the buffer
            photo_size = photo.tell()  # Get the size of the buffer
            photo.seek(0)  # Seek back to the beginning of the buffer
            if photo_size == 0:
                logging.error(f"Photo data is empty for chat ID {chat_id}")
                success = False
                continue

            files = {'photo': photo}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            logging.info(f"Message sent successfully to chat ID: {chat_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram message to chat ID {chat_id}: {e}")
            if response.text:
                logging.error(f"Telegram API response: {response.text}")
            success = False
    return success

def parse_gpu_types(gpu_types: List[str]) -> List[Tuple[str, Optional[float]]]:
    parsed_types = []
    for entry in gpu_types:
        parts = entry.split(",")
        if len(parts) == 2:
            gpu, multiplier = parts
            parsed_types.append((gpu.strip().lower(), float(multiplier)))
        elif len(parts) == 1:
            gpu = parts[0]
            parsed_types.append((gpu.strip().lower(), None))
        else:
            logging.error(f"Invalid GPU entry: {entry}")
    return parsed_types

def get_multiplier(gpu_type: str, gpu_multipliers: List[Tuple[str, Optional[float]]]) -> Optional[float]:
    gpu_type = gpu_type.lower()
    gpu_multipliers = sorted(gpu_multipliers, key=lambda x: len(x[0]), reverse=True)
    for gpu, multiplier in gpu_multipliers:
        if gpu == gpu_type:
            return multiplier
    for gpu, multiplier in gpu_multipliers:
        if gpu in gpu_type:
            return multiplier
    return None

def shorten_id(node_id: str) -> str:
    return f"{node_id[:2]}..{node_id[-2:]}"

def generate_table_image(data: List[List[Any]], headers: List[str]) -> Optional[io.BytesIO]:
    if not data:
        return None  # Return None if there's no data to generate the table

    fig, ax = plt.subplots(figsize=(15, max(len(data) * 0.5, 1)))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=data, colLabels=headers, cellLoc='center', loc='center')

    col_widths = [0.1, 0.08, 0.35, 0.1, 0.1, 0.1, 0.1, 0.1, 0.17]
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

    # Log the size of the generated photo data
    buf.seek(0, 2)  # Seek to the end of the buffer
    photo_size = buf.tell()  # Get the size of the buffer
    buf.seek(0)  # Seek back to the beginning of the buffer
    logging.info(f"Generated photo size: {photo_size} bytes")

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
            if ENABLE_CPU:
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
                if gpu_specs['amount'] > 0 and (any(gpu == gpu_type.lower() for gpu, _ in gpu_multipliers) or any(gpu in gpu_type.lower() for gpu, _ in gpu_multipliers) and (MAX_GPU_PRICE == 0 or gpu_specs['price'] <= MAX_GPU_PRICE)):
                    amount = gpu_specs['amount']
                    price_per_unit = gpu_specs['price']
                    total_price = price_per_unit * amount
                    multiplier = get_multiplier(gpu_type, gpu_multipliers)
                    cost_per_device = price_per_unit

                    if key not in seen_hostnodes:
                        seen_hostnodes.add(key)
                        new_gpu_nodes.append({**hostnode, 'id': key})

                    efficiency = None if multiplier is None else round((multiplier * amount) / total_price, 2)

                    current_gpu_nodes.append({
                        'id': key,
                        'location': f"{hostnode['location']['city']}, {hostnode['location']['country']}",
                        'gpu': gpu_type,
                        'amount': amount,
                        'price': f"${total_price:.2f}",
                        'status': 'Online' if hostnode['status']['online'] else 'Offline',
                        'cost_per_device': f"${cost_per_device:.2f}",
                        'multiplier': multiplier if multiplier else "N/A",
                        'efficiency': efficiency,
                        'calculation': None if multiplier is None else f"({multiplier:.2f} x {amount}) / {total_price:.2f}"
                    })

    else:
        logging.error("API request was not successful")

    if MIN_EFFICIENCY > 0:
        current_gpu_nodes = [node for node in current_gpu_nodes if node['efficiency'] and node['efficiency'] >= MIN_EFFICIENCY]

    combined_data = []
    index = 1
    if ENABLE_CPU:
        for node in current_cpu_nodes:
            combined_data.append([
                index,
                shorten_id(node['id']),
                node['cpu'],
                node['amount'],
                node['price'],
                '-', '-', '-', '-'
            ])
            index += 1

    for node in current_gpu_nodes:
        combined_data.append([
            index,
            shorten_id(node['id']),
            node['gpu'],
            node['amount'],
            node['price'],
            node['cost_per_device'],
            node['multiplier'],
            node['efficiency'],
            node['calculation']
        ])
        index += 1

    headers = ["Index", "ID", "Type", "Amount", "Price ($)", "Cost/Device ($)", "Multiplier", "Efficiency", "Calculation"]

    if combined_data:  # Check if there is data to generate the table
        table_image = generate_table_image(combined_data, headers)
        if table_image and not send_telegram_message(table_image):
            logging.error("Failed to send some Telegram notifications")
    else:
        logging.info("No data available to generate the table image.")

    print(tabulate(combined_data, headers=headers))

    return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes

def handle_error(error: Exception) -> None:
    logging.error(f"An error occurred: {error}")

def notify_new_cpu_nodes(new_cpu_nodes: List[Dict[str, Any]]) -> None:
    logging.info(f"Found {len(new_cpu_nodes)} new hostnodes with {CPU_TYPE} CPU:")
    for node in new_cpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        # logging.info(f"Hostnode ID: {node_id}")

def notify_new_gpu_nodes(new_gpu_nodes: List[Dict[str, Any]]) -> None:
    logging.info(f"Found {len(new_gpu_nodes)} new hostnodes with GPUs up to price {MAX_GPU_PRICE}:")
    for node in new_gpu_nodes:
        node_id = node.get('id', 'Unknown ID')
        # logging.info(f"Hostnode ID: {node_id}")
