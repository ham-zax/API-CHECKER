import json
import os

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
        self.API_URL = config_data["API_URL"]
        self.PARAMS = config_data["PARAMS"]
        self.INTERVAL = config_data["INTERVAL"]
        self.TELEGRAM_TOKEN = config_data["TELEGRAM_TOKEN"]
        self.CHAT_ID = config_data["CHAT_ID"]
        self.CPU_TYPE = config_data["CPU_TYPE"]
        self.MAX_GPU_PRICE = config_data["MAX_GPU_PRICE"]
        self.MIN_EFFICIENCY = config_data["MIN_EFFICIENCY"]
        self.GPU_TYPES = config_data["GPU_TYPES"]

config = Config()
