import os
import time
import cv2
import threading
import config
import socket
import base64
import requests
import RPi.GPIO as GPIO
from flask import Flask, jsonify, render_template, redirect
from dotenv import load_dotenv
import src.utils as utils
from modules.logging import logger
from modules.person_dict import HumanDetection
load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROCESS_URL = os.getenv("PROCESS_URL")
WEB_HOST = os.getenv("WEB_HOST")
WEB_PORT = os.getenv("WEB_PORT")
HOSTNAME = socket.gethostname()

# GPIO Setup
GPIO.setmode(GPIO.BCM)
## GPIO Setup
GPIO.setup(config.PIN_BUZZ, GPIO.OUT)
GPIO.setup(config.PIN_BUZZ_DISABLE_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(config.PIN_R_LED, GPIO.OUT)
GPIO.setup(config.PIN_Y_LED, GPIO.OUT)
GPIO.setup(config.PIN_G_LED, GPIO.OUT)
## GPIO Init
GPIO.output(config.PIN_BUZZ, GPIO.LOW)
GPIO.output(config.PIN_R_LED, GPIO.LOW)
GPIO.output(config.PIN_Y_LED, GPIO.LOW)
GPIO.output(config.PIN_G_LED, GPIO.LOW)

# boot animation
for i in range(0, 3):
    GPIO.output(config.PIN_R_LED, GPIO.HIGH)
    GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
    GPIO.output(config.PIN_G_LED, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(config.PIN_R_LED, GPIO.LOW)
    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
    GPIO.output(config.PIN_G_LED, GPIO.LOW)
    time.sleep(0.5)
GPIO.output(config.PIN_R_LED, GPIO.HIGH)
GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
GPIO.output(config.PIN_G_LED, GPIO.HIGH)
time.sleep(3)
GPIO.output(config.PIN_R_LED, GPIO.LOW)
GPIO.output(config.PIN_Y_LED, GPIO.LOW)
GPIO.output(config.PIN_G_LED, GPIO.LOW)

# thread target
def _capture_target(_capture_delay):
    detector = HumanDetection(config.DETECTION_MODEL_PATH, config.REID_MODEL_PATH, config.DEVICE)
    cap = cv2.VideoCapture("libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        logger.error("카메라를 열 수 없습니다.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("프레임을 가져올 수 없습니다.")
                time.sleep(_capture_delay)
                continue
            
            capture_time = utils.get_now_ftime()
            save_name = f'{capture_time}.jpg'
            save_path = os.path.join(config.CAPTURE_FOLDER_PATH, save_name)
            
            cv2.imwrite(save_path, frame)
            logger.info(f"{save_name} 캡쳐 완료")
            
            # Send image to process server
            print(detector.is_face(save_path)[0])
            if detector.is_face(save_path)[0] == True:
                logger.info(f"{save_name} 얼굴 인식됨")
                GPIO.output(config.PIN_BUZZ, GPIO.HIGH)
                with open(save_path, "rb") as f:
                    image = f.read()
                    image = base64.b64encode(image).decode("utf-8")
                    data = {
                        "service_key": SERVICE_KEY,
                        "image": image,
                        "capture_time": capture_time,
                        "reqHost": HOSTNAME
                    }
                    req_rst = requests.post(f"{PROCESS_URL}/process", data=data)
            else:
                GPIO.output(config.PIN_BUZZ, GPIO.LOW)
                    
            time.sleep(_capture_delay)
            
    cap.release()
threading.Thread(target=_capture_target, args=(0.1,), daemon=True).start()

def _led_matrix_target():
    while True:
        for i in range(0, 4):
            if config.get_status() == config.STATUS_NORMAL:
                GPIO.output(config.PIN_G_LED, GPIO.HIGH)
                GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                GPIO.output(config.PIN_R_LED, GPIO.LOW)
                
            elif config.get_status() == config.STATUS_WARN:
                if i < 2:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
                else:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
                
            elif config.get_status() == config.STATUS_ERROR:
                GPIO.output(config.PIN_G_LED, GPIO.LOW)
                GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                GPIO.output(config.PIN_R_LED, GPIO.HIGH)
                
            elif config.get_status() == config.STATUS_CRITICAL:
                if i < 2:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.HIGH)
                else:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
            
            time.sleep(0.5)
threading.Thread(target=_led_matrix_target, daemon=True).start()

def _buzz_target():
    config.set_status(config.STATUS_WARN)
    GPIO.output(config.PIN_BUZZ, GPIO.HIGH)
    logger.info("경보기가 작동했습니다.")
    
    disable_stack = 0
    while True:
        if (GPIO.input(config.PIN_BUZZ_DISABLE_BTN) == GPIO.HIGH) or (config.get_status() == config.STATUS_NORMAL):
            disable_stack += 1
        else:
            disable_stack = 0
        
        if disable_stack >= 30:
            config.set_status(config.STATUS_NORMAL)
            GPIO.output(config.PIN_BUZZ, GPIO.LOW)
            logger.info("경보기가 해제되었습니다.")
            return
        
        time.sleep(0.1)

# flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/buzz", methods=["GET"])
def buzz():
    if config.get_status() == config.STATUS_ERROR:
        return redirect("/")
    threading.Thread(target=_buzz_target, daemon=True).start()
    return redirect("/")

@app.route("/buzz_off", methods=["GET"])
def buzz_off():
    config.set_status(config.STATUS_NORMAL)
    GPIO.output(config.PIN_BUZZ, GPIO.LOW)
    logger.info("경보기가 해제되었습니다.")
    
    return redirect("/")

@app.route("/last_capture", methods=["GET"])
def last_capture():
    captures = os.listdir(config.CAPTURE_FOLDER_PATH)
    captures.sort(reverse=True)
    if len(captures) == 0:
        return jsonify({"message": "No captures"})
    last_capture = captures[0]
    with open(os.path.join(config.CAPTURE_FOLDER_PATH, last_capture), "rb") as f:
        image = f.read()
        image = base64.b64encode(image).decode("utf-8")
        return jsonify({"last_capture": last_capture.split('.')[0] , "image": image})

if __name__ == "__main__":
    app.run(host=WEB_HOST, port=WEB_PORT, debug=True)