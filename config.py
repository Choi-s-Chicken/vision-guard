import json
import os
import socket
import platform
from dotenv import load_dotenv
load_dotenv()

# Product info
PRCT_MODEL = os.environ["PRCT_MODEL"]
PRCT_SERIAL = os.environ["PRCT_SERIAL"]
PROCESS_URL = os.environ["PROCESS_URL"]
FLATFORM = platform.system()
HOSTNAME = socket.gethostname()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "src", "models")
DB_FOLDER_PATH = os.path.join(BASE_DIR, 'db')
LOG_PATH = os.path.join(DB_FOLDER_PATH, "main.log")
USER_DB_PATH = os.path.join(DB_FOLDER_PATH, "user.db")
CAPTURE_FOLDER_PATH = os.path.join(DB_FOLDER_PATH, "captures")

# OpenVINO
DEVICE = "CPU"
DETECTION_MODEL_PATH = os.path.join(MODEL_PATH, "face-detection-adas-0001")
REID_MODEL_PATH = os.path.join(MODEL_PATH, "face-reidentification-retail-0095")

# Pins
PIN_ALARM = 23
PIN_ALARM_BTN = 24
PIN_R_LED = 22
PIN_Y_LED = 27
PIN_G_LED = 17

# Status
STATUS_NORMAL = "normal"
STATUS_WARN   = "warning"
STATUS_ERROR  = "error"
STATUS_CRITI  = "critical"

# Config
config_path = os.path.join(DB_FOLDER_PATH, "config.json")

def get_config(key:str):
    with open(config_path, "r") as f:
        return json.load(f)[key]

def set_config(key, value):
    with open(config_path, "r") as f:
        config = json.load(f)
    
    config[key] = value
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)