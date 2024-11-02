import json
import os
import socket
import platform
import sqlite3
from dotenv import load_dotenv
load_dotenv()

# Product info
PRCT_MODEL = os.environ["PRCT_MODEL"]
PRCT_SERIAL = os.environ["PRCT_SERIAL"]
CONNECT_KEY = os.environ["PRCT_CONNECT_KEY"]
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
CONFIG_DB_PATH = os.path.join(DB_FOLDER_PATH, "config.db")

def get_config(key: str, _default=None):
    conn = sqlite3.connect(CONFIG_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else _default

def set_config(key, value):
    conn = sqlite3.connect(CONFIG_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, json.dumps(value)))
    conn.commit()
    conn.close()