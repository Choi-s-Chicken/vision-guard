import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "src", "models")
DB_FOLDER_PATH = os.path.join(BASE_DIR, 'db')
CAPTURE_FOLDER_PATH = os.path.join(DB_FOLDER_PATH, "captures")

