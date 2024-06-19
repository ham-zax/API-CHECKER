from typing import List, Dict, Tuple, Optional, Any
from config import config
import logging
from tabulate import tabulate
import matplotlib.pyplot as plt
import io

from notifier import send_telegram_message

logging.basicConfig(level=logging.INFO)

def parse_gpu_types(gpu_types: List[str]) -> List[Tuple[str, Optional[float]]]:
    """Parse GPU types into a list of tuples with optional multipliers."""
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
    """Retrieve the multiplier for a given GPU type."""
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
    """Shorten the node ID for display purposes."""
    return f"{node_id[:2]}..{node_id[-2:]}"

def generate_table_image(data: List[List[Any]], headers: List[str]) -> io.BytesIO:
    """Generate an image of a table using matplotlib."""
    fig, ax = plt.subplots(figsize=(15, len(data) * 0.5))
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

    return buf

def process_response(data: Dict[str, Any], seen_hostnodes: set) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Process the API response and categorize nodes."""
    new_cpu_nodes = []
    new_gpu_nodes = []
    current_cpu_nodes = []
    current_gpu_nodes = []

    gpu_multipliers = parse_gpu_types(config.GPU_TYPES)

    if not data.get("success"):
        logging.error("API request was not successful")
        return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes

    hostnodes = data.get("hostnodes", {})
    for key, hostnode in hostnodes.items():
        cpu_info = hostnode['specs']['cpu']
        if config.CPU_TYPE in cpu_info['type']:
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
            if gpu_specs['amount'] > 0 and (any(gpu == gpu_type.lower() for gpu, _ in gpu_multipliers) or any(gpu in gpu_type.lower() for gpu, _ in gpu_multipliers) and (config.MAX_GPU_PRICE == 0 or gpu_specs['price'] <= config.MAX_GPU_PRICE)):
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

    if config.MIN_EFFICIENCY > 0:
        current_gpu_nodes = [node for node in current_gpu_nodes if node['efficiency'] and node['efficiency'] >= config.MIN_EFFICIENCY]

    combined_data = []
    index = 1
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
    table_image = generate_table_image(combined_data, headers)

    if not send_telegram_message(table_image):
        logging.error("Failed to send some Telegram notifications")

    print(tabulate(combined_data, headers=headers))

    return new_cpu_nodes, current_cpu_nodes, new_gpu_nodes, current_gpu_nodes
