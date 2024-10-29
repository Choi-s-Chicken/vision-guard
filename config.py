import json
import os

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

def get_status():
    with open(os.path.join(DB_FOLDER_PATH, "config.json"), "r") as f:
        return json.load(f)["status"]

def set_status(status):
    with open(os.path.join(DB_FOLDER_PATH, "config.json"), "w") as f:
        json.dump({"status": status}, f)