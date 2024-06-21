# api_checker/config.py
API_URL = "https://dashboard.tensordock.com/api/session/deploy/hostnodes"
PARAMS = {
    'minvCPUs': 1,
    'minStorage': 20
}
INTERVAL = 60 # Interval in seconds

TELEGRAM_TOKEN = '7119782068:AAHm5qatChCeyaHdNmlt6FBGF8NxVxj0OV4'
CHAT_ID = '376895924'
# Configuration for CPU and GPU search
CPU_TYPE = "8995"
MAX_GPU_PRICE = 0  # Set the maximum price for GPU filtering; 0 means no filtering
MIN_EFFICIENCY = 3
GPU_TYPES = [
    "3050,0.1",
    "3060,0.1",
    "3070,0.1",
    "3080,0.1",
    "3080Ti,0.25",
    "3090,0.25",
    "4050,0.25",
    "4060,0.25",
    "4070,0.25",
    "4080,0.25",
    "4090,1",
    "4000,0.25",
    "A4000,0.25",
    "4000Ada,0.25",
    "5000,0.25",
    "A5000,0.25",
    "5000Ada,1",
    "A6000,1",
    "6000Ada,1",
    "8000,1",
    "A10,1",
    "A10G,1",
    "A16,1",
    "A30,1",
    "A40,2",
    "T4,0.25",
    "L40,2",
    "L4,1",
    "L40S,2",
    "P100 PCIe,0.25",
    "V100-SXM2,0.25",
    "V100-SXM2-32,0.5",
    "V100-PCIE,0.25",
    "V100-PCIE,0.5",
    "V100S-PCIE,1",
    "A100-SXM4,2.5",
    "A100-SXM4-80,5",
    "A100-PCIE,2",
    "A100-PCIe-80,5",
    "A100-NVLink-80,5",
    "H100,10",
]
