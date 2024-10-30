import base64
import os
import time

import requests
import config
import cv2
import src.utils as utils
import modules.gpio_control as gpio_ctrl
from modules.logging import logger

def _led_control_target():
    while True:
        for i in range(0, 2):
            if config.get_config('status') == config.STATUS_NORMAL:
                gpio_ctrl.control_led(green=True, yellow=False, red=False)
                
            elif config.get_config('status') == config.STATUS_WARN:
                if i == 0:
                    gpio_ctrl.control_led(green=False, yellow=True, red=False)
                else:
                    gpio_ctrl.control_led(green=False, yellow=False, red=False)
                
            elif config.get_config('status') == config.STATUS_ERROR:
                gpio_ctrl.control_led(green=False, yellow=True, red=False)
                
            elif config.get_config('status') == config.STATUS_CRITI:
                if i == 0:
                    gpio_ctrl.control_led(green=False, yellow=False, red=True)
                else:
                    gpio_ctrl.control_led(green=False, yellow=False, red=False)
            
            time.sleep(0.25)

def _capture_target(_capture_delay):
    # Camera load
    while True:
        cap = cv2.VideoCapture("0")
        if cap.isOpened():
            config.set_config('status', config.STATUS_NORMAL)
            config.set_config('camera_ready', True)
        else:
            config.set_config('status', config.STATUS_CRITI)
            config.set_config('camera_ready', False)
            logger.error("카메라를 열 수 없습니다.")
        
        if config.get_config('camera_ready') == False:
            logger.error("카메라가 준비되지 않아 재시도합니다.")
            time.sleep(10)
            continue
        
        break
    
    # Capture frame
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("프레임을 가져올 수 없습니다.")
            time.sleep(_capture_delay)
            continue
        
        # Send data to process server
        capture_time = utils.get_now_ftime()
        req_data = {
            "serial": config.PRCT_SERIAL,
            "capture_time": capture_time,
            "capture_data": base64.encode.b64encode(frame)
        }
        
        req_rst = requests.post(config.PROCESS_URL, json=req_data)
                
        time.sleep(_capture_delay)
            
    cap.release()

def _alarm_turnon_target():
    if config.get_config('alarm') == True:
        logger.error("경보기가 이미 작동 중입니다. 작업이 거부되었습니다.")
        return
    
    config.set_config('alarm', True)
    config.set_config('status', config.STATUS_WARN)
    gpio_ctrl.control_alarm(True)
    logger.info("경보기를 작동했습니다.")
    
    disable_stack = 0
    while True:
        if gpio_ctrl.alarm_btn_status() == gpio_ctrl.HIGH:
            disable_stack += 1
        else:
            disable_stack = 0
        
        if disable_stack >= 30 or config.get_config('alarm') == False:
            config.set_config('status', config.STATUS_NORMAL)
            config.set_config('alarm', False)
            gpio_ctrl.control_alarm(False)
            logger.info("경보기가 해제되었습니다.")
            return
        
        time.sleep(0.1)

def _reboot_target():
    for i in range(0, 3):
        gpio_ctrl.control_led(green=True, yellow=True, red=True)
        time.sleep(0.5)
        gpio_ctrl.control_led(green=False, yellow=False, red=False)
        time.sleep(0.5)
    os.system("sudo reboot now")
