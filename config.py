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

# Status
STATUS_NORMAL = "normal"
STATUS_WARN   = "warn"
STATUS_ERROR  = "error"
STATUS = "NORMAL"