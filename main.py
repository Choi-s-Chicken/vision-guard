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

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROCESS_URL = os.getenv("PROCESS_URL")
WEB_HOST = os.getenv("WEB_HOST")
WEB_PORT = os.getenv("WEB_PORT")

# GPIO Setup
## GPIO Init
gpio_ctrl.gpio_init()
gpio_ctrl.control_led(green=False, yellow=False, red=False)
config.set_config('status', config.STATUS_NORMAL)

# boot animation
for i in range(0, 3):
    gpio_ctrl.control_led(green=True, yellow=True, red=True)
    time.sleep(0.3)
    gpio_ctrl.control_led(green=False, yellow=False, red=False)
    time.sleep(0.3)
gpio_ctrl.control_led(green=True, yellow=True, red=True)
time.sleep(3)
gpio_ctrl.control_led(green=False, yellow=False, red=False)

# capture target
def _capture_target(_capture_delay):
    while True:        
        subprocess.run(["libcamera-jpeg", "-o", "capture.jpg"])
        
        # Read the captured image
        if os.path.exists("capture.jpg") == False:
            config.set_config('status', config.STATUS_CRITI)
            logger.error("사진 정보 얻기에 실패했습니다.")
            time.sleep(_capture_delay)
            continue
        config.set_config('status', config.STATUS_NORMAL)
        logger.info("사진을 촬영했습니다.")
        
        with open("capture.jpg", "rb") as image_file:
            frame = image_file.read()
        
        # Send data to process server
        capture_time = utils.get_now_ftime()
        req_data = {
            "serial": config.PRCT_SERIAL,
            "capture_time": capture_time,
            "capture_data": base64.b64encode(frame).decode('utf-8')
        }
        
        try:
            req_rst = requests.post(config.PROCESS_URL, json=req_data, timeout=3)
            req_rst.raise_for_status()
            config.set_config('status', config.STATUS_NORMAL)
            logger.info("서버로 사진을 전송했습니다.")
        except:
            config.set_config('status', config.STATUS_ERROR)
            logger.error("서버와 통신 중 문제가 발생했습니다.")
            time.sleep(_capture_delay)
            continue
        
        os.remove("capture.jpg")
    
        time.sleep(_capture_delay)
# thread start
threading.Thread(target=targets._led_control_target, daemon=True).start()
threading.Thread(target=_capture_target, args=(1,), daemon=True).start()

# WebService Start
vg_web_app = VGApp()
vg_web_app.run(WEB_HOST, WEB_PORT, _debug=True)
