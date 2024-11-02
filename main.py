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

# capture target
def _capture_target(_capture_delay):
    while True:        
        capture_success = False
        while not capture_success:
            try:
                subprocess.run(["libcamera-jpeg", "-o", "capture.jpg"], check=True)
            except subprocess.CalledProcessError as e:
                config.set_config('status', config.STATUS_ERROR)
                logger.error(f"사진 정보 얻기에 실패했습니다: {e}")
                time.sleep(_capture_delay)
                continue
            
            # Read the captured image
            if not os.path.exists("capture.jpg"):
                config.set_config('status', config.STATUS_ERROR)
                logger.error("사진 정보 얻기에 실패했습니다.")
                time.sleep(_capture_delay)
            else:
                capture_success = True
                config.set_config('status', config.STATUS_NORMAL)
                logger.info("사진을 촬영했습니다.")
                
        with open("capture.jpg", "rb") as image_file:
            frame = image_file.read()
            
        # Send data to process server
        capture_time = utils.get_now_ftime()
        req_data = {
            "serial": config.PRCT_SERIAL,
            "connect_key": config.CONNECT_KEY,
            "status": config.get_config('status'),
            "is_alarm": config.get_config('alarm'),
            "reboot_poss": config.get_config('reboot_poss'),
            "alarm_poss": config.get_config('alarm_poss'),
            "capture_time": capture_time,
            "capture_data": base64.b64encode(frame).decode('utf-8'),
        }
        
        retry_count = 0
        while True:
            retry_count += 1
            if retry_count > config.get_config('api_error_max_retry'):
                config.set_config('status', config.STATUS_CRITI)
                logger.critical("서버와 통신을 실패했습니다.")
                break
            
            try:
                req_rst = requests.post(f"{config.PROCESS_URL}/device/data-process", json=req_data, timeout=3)
                req_rst.raise_for_status()
                config.set_config('status', config.STATUS_NORMAL)
                logger.info("서버와 통신했습니다.")
                
                res_data = req_rst.json()
                res_config_data = res_data.get('server_device_status', '-999')
                
                if res_config_data != '-999':
                    alarm = res_config_data.get('alarm', '-999')
                    disable_alarm = res_config_data.get('disable_alarm', '-999')
                    if alarm != '-999':
                        if disable_alarm != True:
                            threading.Thread(target=targets._alarm_turnon_target, daemon=True).start()
                    if disable_alarm != '-999':
                        if disable_alarm == True:
                            config.set_config('alarm', False)
                        
                    reboot_possible = res_config_data.get('reboot_possible', '-999')
                    alarm_possible = res_config_data.get('alarm_possible', '-999')
                    if reboot_possible != '-999':
                        config.set_config('reboot_poss', reboot_possible)
                    if alarm_possible != '-999':
                        config.set_config('alarm_poss', alarm_possible)
                        
                    last_server_connect_time = res_config_data.get('last_connection', '-999')
                    if last_server_connect_time != '-999':
                        config.set_config('last_server_connect_time', last_server_connect_time)
                
                
                
            except requests.RequestException as e:
                config.set_config('status', config.STATUS_ERROR)
                logger.error(f"서버와 통신 중 문제가 발생했습니다. 재시도 중... ({retry_count}/{config.get_config('api_error_max_retry')}): {e}")
                time.sleep(_capture_delay)
                continue
        
        if os.path.exists("capture.jpg"):
            os.remove("capture.jpg")
    
        time.sleep(_capture_delay)

# thread start
threading.Thread(target=targets._led_control_target, daemon=True).start()
threading.Thread(target=_capture_target, args=(0,), daemon=True).start()

# WebService Start
vg_web_app = VGApp()
vg_web_app.run(WEB_HOST, WEB_PORT, _debug=True)
