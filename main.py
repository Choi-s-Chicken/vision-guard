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
    # # Camera load
    # while True:
    #     cap = cv2.VideoCapture(0)
    #     if cap.isOpened():
    #         config.set_config('status', config.STATUS_NORMAL)
    #         config.set_config('camera_ready', True)
    #     else:
    #         config.set_config('status', config.STATUS_CRITI)
    #         config.set_config('camera_ready', False)
    #         logger.error("카메라를 열 수 없습니다.")
        
    #     if config.get_config('camera_ready') == False:
    #         logger.error("카메라가 준비되지 않아 10초 후 재시도합니다.")
    #         time.sleep(10)
    #         continue
        
    #     break
    
    # Capture frame
    while True:
        # ret, frame = cap.read()
        # if not ret:
        #     logger.error("프레임을 가져올 수 없습니다.")
        #     time.sleep(_capture_delay)
        #     continue
        
        subprocess.run(["libcamera-jpeg", "-o", "capture.jpg"])
        
        # Read the captured image
        if os.exists("capture.jpg") == False:
            logger.error("사진 정보를 읽을 수 없습니다.")
            config.set_config('status', config.STATUS_CRITI)
            time.sleep(_capture_delay)
            continue
        
        with open("capture.jpg", "rb") as image_file:
            frame = image_file.read()
        
        # Send data to process server
        capture_time = utils.get_now_ftime()
        req_data = {
            "serial": config.PRCT_SERIAL,
            "capture_time": capture_time,
            "capture_data": base64.encode.b64encode(frame)
        }
        
        req_rst = requests.post(config.PROCESS_URL, json=req_data)
        
        os.remove("capture.jpg")
                
        time.sleep(_capture_delay)
            
    cap.release()
# thread start
threading.Thread(target=targets._led_control_target, daemon=True).start()
threading.Thread(target=_capture_target, args=(0.1,), daemon=True).start()

# WebService Start
vg_web_app = VGApp()
vg_web_app.run(WEB_HOST, WEB_PORT, _debug=True)
