class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        self.API_URL = "https://dashboard.tensordock.com/api/session/deploy/hostnodes"
        self.PARAMS = {
            'minvCPUs': 1,
            'minStorage': 20
        }
        self.INTERVAL = 180  # Interval in seconds
        self.TELEGRAM_TOKEN = '7119782068:AAHm5qatChCeyaHdNmlt6FBGF8NxVxj0OV4'
        self.CHAT_ID = '376895924'
        self.CPU_TYPE = "3995"
        self.MAX_GPU_PRICE = 0  # Set the maximum price for GPU filtering; 0 means no filtering
        self.MIN_EFFICIENCY = 2
        self.GPU_TYPES = [
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

config = Config()