import os
import time
import cv2
import threading
import config
import socket
import base64
import requests
from flask import Flask, request, jsonify
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

def _capture_target(_capture_delay):
    detector = HumanDetection(config.DETECTION_MODEL_PATH, config.REID_MODEL_PATH, config.DEVICE)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("카메라를 열 수 없습니다.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("프레임을 가져올 수 없습니다.")
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
                    
            time.sleep(_capture_delay)
            
    cap.release()
threading.Thread(target=_capture_target, args=(0.1,), daemon=True).start()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "잘 작동되고 있습니다."

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
    app.run(host=WEB_HOST, port=WEB_PORT)