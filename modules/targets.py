import base64
import os
import subprocess
import threading
import time
import src.utils as utils
import modules.targets as targets

import requests
import config
import modules.gpio_control as gpio_ctrl
from modules.logging import logger

def _led_control_target():
    # boot animation
    for i in range(0, 3):
        gpio_ctrl.control_led(green=True, yellow=True, red=True)
        time.sleep(0.3)
        gpio_ctrl.control_led(green=False, yellow=False, red=False)
        time.sleep(0.3)
    gpio_ctrl.control_led(green=True, yellow=True, red=True)
    time.sleep(3)
    gpio_ctrl.control_led(green=False, yellow=False, red=False)
    
    detail = 10
    while True:
        try:
            for i in range(0, detail+1):
                status = config.get_config('status')
                gpio_ctrl.control_led(green=False, yellow=False, red=False)
                
                if status == config.STATUS_NORMAL:
                    gpio_ctrl.control_led(green=True)
                    
                elif status == config.STATUS_WARN:
                    gpio_ctrl.control_led(yellow=True)
                    
                elif status == config.STATUS_ERROR:
                    gpio_ctrl.control_led(red=True)
                    
                elif status == config.STATUS_CRITI:
                    if i < int((detail / 2)):
                        gpio_ctrl.control_led(red=True)
                    else:
                        gpio_ctrl.control_led(red=False)

                if config.get_config('alarm') == True:
                    if i < int((detail / 2)):
                        gpio_ctrl.control_led(yellow=True)
                    else:
                        gpio_ctrl.control_led(yellow=False)

                time.sleep(0.15)
        except Exception as e:
            logger.error(f"LED control error: {e}")

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
                logger.critical("서버에 사진 전송을 실패했습니다.")
                break
            
            try:
                req_rst = requests.get(f"{config.PROCESS_URL}/device/data-process", json=req_data, timeout=3)
                req_rst.raise_for_status()
                config.set_config('status', config.STATUS_NORMAL)
                logger.info("서버에 사진을 전송했습니다.")
                break
                
            except Exception as e:
                config.set_config('status', config.STATUS_ERROR)
                logger.error(f"서버에 사진을 전송하는 중 문제가 발생했습니다. 재시도 중... ({retry_count}/{config.get_config('api_error_max_retry')}): {e}")
                time.sleep(_capture_delay)
                continue
        
        if os.path.exists("capture.jpg"):
            os.remove("capture.jpg")
    
        time.sleep(_capture_delay)

def _server_device_status_update_target(_req_delay):
    while True:
        req_data = {
            "serial": config.PRCT_SERIAL,
            "connect_key": config.CONNECT_KEY
        }
        
        retry_count = 0
        while True:
            retry_count += 1
            if retry_count > config.get_config('api_error_max_retry'):
                config.set_config('status', config.STATUS_CRITI)
                logger.critical("서버와 통신을 실패했습니다.")
                break
            
            try:
                req_rst = requests.get(f"{config.PROCESS_URL}/device/get-status", json=req_data, timeout=3)
                req_rst.raise_for_status()
                config.set_config('status', config.STATUS_NORMAL)
                logger.info("서버와 통신했습니다.")
                res_data = req_rst.json()
                
                if res_data.get('status', 'error') != 'success':
                    logger.error("서버와 통신 중 문제가 발생했습니다.")
                    break
                
                res_config_data = res_data.get('server_device_status', '-999')
                
                if res_config_data != '-999':
                    alarm = res_config_data.get('alarm', '-999')
                    if alarm != '-999':
                        if alarm == True:
                            threading.Thread(target=targets._alarm_turnon_target, daemon=True).start()
                        else:
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
                
                break
                
            except Exception as e:
                config.set_config('status', config.STATUS_ERROR)
                logger.error(f"서버와 통신 중 문제가 발생했습니다. 재시도 중... ({retry_count}/{config.get_config('api_error_max_retry')}): {e}")
                time.sleep(_req_delay)
                continue
        
        time.sleep(_req_delay)

def _reservice_target():
    for i in range(0, 3):
        gpio_ctrl.control_led(green=True, yellow=True, red=True)
        time.sleep(0.2)
        gpio_ctrl.control_led(green=False, yellow=False, red=False)
        time.sleep(0.2)
    logger.info("서비스를 재시작합니다.")
    gpio_ctrl.control_alarm(False)
    gpio_ctrl.control_led(green=False, yellow=False, red=False)
    os.system("sudo systemctl restart vg")
    
def _reboot_target():
    for i in range(0, 3):
        gpio_ctrl.control_led(green=True, yellow=True, red=True)
        time.sleep(0.5)
        gpio_ctrl.control_led(green=False, yellow=False, red=False)
        time.sleep(0.5)
    logger.info("시스템을 재부팅합니다.")
    gpio_ctrl.control_alarm(False)
    gpio_ctrl.control_led(green=False, yellow=False, red=False)
    os.system("sudo reboot now")