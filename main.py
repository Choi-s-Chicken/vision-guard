import base64
import os
import subprocess
import time
import threading

import cv2
import requests
import config
import src.utils as utils
from modules.logging import logger
import modules.gpio_control as gpio_ctrl
from webservice.main import VGApp
import modules.targets as targets

WEB_HOST = os.getenv("WEB_HOST")
WEB_PORT = os.getenv("WEB_PORT")

# GPIO Setup
## GPIO Init
gpio_ctrl.gpio_init()
gpio_ctrl.control_led(green=False, yellow=False, red=False)
config.set_config('status', config.STATUS_NORMAL)
config.set_config('alarm', False)

# thread start
threading.Thread(target=targets._led_control_target, daemon=True).start()
threading.Thread(target=targets._capture_target, args=(0,), daemon=True).start()
threading.Thread(target=targets._server_device_status_update_target, args=(1,), daemon=True).start()

# WebService Start
vg_web_app = VGApp()
vg_web_app.run(WEB_HOST, WEB_PORT, _debug=True)
