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
GPU_TYPE = "4090"
MAX_GPU_PRICE = 0.4