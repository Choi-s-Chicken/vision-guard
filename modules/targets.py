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
    detail = 20
    while True:
        for i in range(0, detail):
            if config.get_config('status') == config.STATUS_NORMAL:
                gpio_ctrl.control_led(green=True, yellow=False, red=False)
                
            elif config.get_config('status') == config.STATUS_WARN:
                gpio_ctrl.control_led(yellow=True)
                
            elif config.get_config('status') == config.STATUS_ERROR:
                gpio_ctrl.control_led(green=False, yellow=False, red=True)
                
            elif config.get_config('status') == config.STATUS_CRITI:
                if i < (detail/2):
                    gpio_ctrl.control_led(green=False, yellow=False, red=True)
                else:
                    gpio_ctrl.control_led(green=False, yellow=False, red=False)
            
            if config.get_config('alarm') == True:
                if i < (detail/2):
                    gpio_ctrl.control_led(yellow=True)
                else:
                    gpio_ctrl.control_led(yellow=False)
            
            time.sleep(0.05)

def _alarm_turnon_target():
    if config.get_config('alarm') == True:
        logger.error("경보기가 이미 작동 중입니다. 작업이 거부되었습니다.")
        return
    
    config.set_config('alarm', True)
    gpio_ctrl.control_alarm(True)
    logger.info("경보기를 작동했습니다.")
    
    disable_stack = 0
    while True:
        if gpio_ctrl.alarm_btn_status() == gpio_ctrl.HIGH:
            disable_stack += 1
        else:
            disable_stack = 0
        
        if disable_stack >= 30 or config.get_config('alarm') == False:
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
