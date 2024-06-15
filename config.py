# api_checker/config.py
API_URL = "https://dashboard.tensordock.com/api/session/deploy/hostnodes"
PARAMS = {
    'minvCPUs': 1,
    'minStorage': 20
}
INTERVAL = 180  # Interval in seconds

TELEGRAM_TOKEN = '7119782068:AAHm5qatChCeyaHdNmlt6FBGF8NxVxj0OV4'
CHAT_ID = '376895924'
# Configuration for CPU and GPU search
CPU_TYPE = "3995"
GPU_TYPES = ["A40,2","A4000,0.25", "l4,1", "l40,2","4090,1","3080,0.25"]  # Define GPU types and their multipliers directly
MAX_GPU_PRICE = 0  # Set the maximum price for GPU filtering; 0 means no filtering

# GPU Multiplier lookup
GPU_MULTIPLIERS = {
    "GeForce RTX 3050": 0.1,
    "GeForce RTX 3050 Ti": 0.1,
    "GeForce RTX 3060": 0.1,
    "GeForce RTX 3060 Ti": 0.1,
    "GeForce RTX 3070": 0.1,
    "GeForce RTX 3070 Ti": 0.1,
    "GeForce RTX 3080": 0.1,
    "GeForce RTX 3080 Ti": 0.25,
    "GeForce RTX 3090": 0.25,
    "GeForce RTX 3090 Ti": 0.25,
    "GeForce RTX 4050": 0.25,
    "GeForce RTX 4060": 0.25,
    "GeForce RTX 4060 Ti": 0.25,
    "GeForce RTX 4070": 0.25,
    "GeForce RTX 4070 Ti": 0.25,
    "GeForce RTX 4070 SUPER": 0.25,
    "GeForce RTX 4070 Ti SUPER": 0.25,
    "GeForce RTX 4080": 0.25,
    "GeForce RTX 4080 SUPER": 0.25,
    "GeForce RTX 4090": 1,
    "GeForce RTX 4090 D": 1,
    "RTX 4000": 0.25,
    "RTX A4000": 0.25,
    "RTX 4000 SFF Ada Generation": 0.25,
    "RTX 5000": 0.25,
    "RTX A5000": 0.25,
    "RTX 5000 Ada Generation": 1,
    "RTX A6000": 1,
    "RTX 6000 Ada Generation": 1,
    "RTX 8000": 1,
    "A10": 1,
    "A10G": 1,
    "A16": 1,
    "A30": 1,
    "A40": 2,
    "A40-8Q": 2,
    "A40 PCIe": 2,
    "Tesla T4": 0.25,
    "L40": 2,
    "L4": 1,
    "L40S": 2,
    "Tesla P100 PCIe": 0.25,
    "Tesla V100-SXM2-16GB": 0.25,
    "Tesla V100-SXM2-32GB": 0.5,
    "Tesla V100-PCIE-16GB": 0.25,
    "Tesla V100-PCIE-32GB": 0.5,
    "Tesla V100S-PCIE-32GB": 1,
    "A100-SXM4-40GB": 2.5,
    "A100-SXM4-80GB": 5,
    "A100-PCIE-40GB": 2,
    "A100 80G PCIe NVLink": 5,
    "A100 80GB NVLink": 5,
    "A100 80GB PCIe": 5,
    "H100 PCIe": 10,
    "H100 80G PCIe": 10,
    "H100 80GB HBM3": 10
}