# api_checker/config.py
API_URL = "https://dashboard.tensordock.com/api/session/deploy/hostnodes"
PARAMS = {
    'maxGPUCount': 0,
    'minRAM': 4,
    'minvCPUs': 1,
    'minStorage': 20
}
INTERVAL = 60  # Interval in seconds
