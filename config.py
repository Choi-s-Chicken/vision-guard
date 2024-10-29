import json
import os
import socket
import platform 

MODEL = "VG01"
SERIAL = "169d236880ae"
FLATFORM = platform.system()
HOSTNAME = socket.gethostname()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "src", "models")
DB_FOLDER_PATH = os.path.join(BASE_DIR, 'db')
CAPTURE_FOLDER_PATH = os.path.join(DB_FOLDER_PATH, "captures")

# OpenVINO
DEVICE = "CPU"
DETECTION_MODEL_PATH = os.path.join(MODEL_PATH, "face-detection-adas-0001")
REID_MODEL_PATH = os.path.join(MODEL_PATH, "face-reidentification-retail-0095")

# Pins
PIN_BUZZ = 23
PIN_BUZZ_DISABLE_BTN = 24
PIN_R_LED = 22
PIN_Y_LED = 27
PIN_G_LED = 17

# Status
STATUS_NORMAL = "normal"
STATUS_WARN   = "warning"
STATUS_ERROR  = "error"
STATUS_CRITI  = "critical"

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