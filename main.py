import os
import time
import cv2
import threading
import config
import socket
import base64
import requests
import RPi.GPIO as GPIO
from flask import Flask, flash, jsonify, render_template, redirect, request, session, url_for
from dotenv import load_dotenv
from auth import login_required, check_login
import src.utils as utils
from modules.logging import logger
from modules.person_dict import HumanDetection
load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")
PROCESS_URL = os.getenv("PROCESS_URL")
WEB_HOST = os.getenv("WEB_HOST")
WEB_PORT = os.getenv("WEB_PORT")

# GPIO Setup
GPIO.setmode(GPIO.BCM)
## GPIO Setup
GPIO.setup(config.PIN_BUZZ, GPIO.OUT)
GPIO.setup(config.PIN_BUZZ_DISABLE_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(config.PIN_R_LED, GPIO.OUT)
GPIO.setup(config.PIN_Y_LED, GPIO.OUT)
GPIO.setup(config.PIN_G_LED, GPIO.OUT)
## GPIO Init
config.set_config('status', config.STATUS_NORMAL)
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
# GPIO.output(config.PIN_R_LED, GPIO.HIGH)
# GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
# GPIO.output(config.PIN_G_LED, GPIO.HIGH)
# time.sleep(3)
# GPIO.output(config.PIN_R_LED, GPIO.LOW)
# GPIO.output(config.PIN_Y_LED, GPIO.LOW)
# GPIO.output(config.PIN_G_LED, GPIO.LOW)

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
                        "reqHost": config.HOSTNAME
                    }
                    req_rst = requests.post(f"{PROCESS_URL}/process", data=data)
            else:
                GPIO.output(config.PIN_BUZZ, GPIO.LOW)
                    
            time.sleep(_capture_delay)
            
    cap.release()
threading.Thread(target=_capture_target, args=(0.1,), daemon=True).start()

def _led_matrix_target():
    while True:
        for i in range(0, 2):
            if config.get_config('status') == config.STATUS_NORMAL:
                GPIO.output(config.PIN_G_LED, GPIO.HIGH)
                GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                GPIO.output(config.PIN_R_LED, GPIO.LOW)
                
            elif config.get_config('status') == config.STATUS_WARN:
                if i == 0:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
                else:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
                
            elif config.get_config('status') == config.STATUS_ERROR:
                GPIO.output(config.PIN_G_LED, GPIO.LOW)
                GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                GPIO.output(config.PIN_R_LED, GPIO.HIGH)
                
            elif config.get_config('status') == config.STATUS_CRITI:
                if i == 0:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.HIGH)
                else:
                    GPIO.output(config.PIN_G_LED, GPIO.LOW)
                    GPIO.output(config.PIN_Y_LED, GPIO.LOW)
                    GPIO.output(config.PIN_R_LED, GPIO.LOW)
            
            time.sleep(0.25)
threading.Thread(target=_led_matrix_target, daemon=True).start()

def _buzz_target():
    config.set_config('status', config.STATUS_WARN)
    GPIO.output(config.PIN_BUZZ, GPIO.HIGH)
    logger.info("경보기가 작동했습니다.")
    
    disable_stack = 0
    while True:
        if (GPIO.input(config.PIN_BUZZ_DISABLE_BTN) == GPIO.HIGH) or (config.get_config('status') == config.STATUS_NORMAL):
            disable_stack += 1
        else:
            disable_stack = 0
        
        if disable_stack >= 30:
            config.set_config('status', config.STATUS_NORMAL)
            GPIO.output(config.PIN_BUZZ, GPIO.LOW)
            logger.info("경보기가 해제되었습니다.")
            return
        
        time.sleep(0.1)

def _reboot_target():
    for i in range(0, 3):
        GPIO.output(config.PIN_R_LED, GPIO.HIGH)
        GPIO.output(config.PIN_Y_LED, GPIO.HIGH)
        GPIO.output(config.PIN_G_LED, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(config.PIN_R_LED, GPIO.LOW)
        GPIO.output(config.PIN_Y_LED, GPIO.LOW)
        GPIO.output(config.PIN_G_LED, GPIO.LOW)
        time.sleep(0.2)
    os.system("sudo reboot now")

# flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html", prct_model=config.MODEL, prct_serial=config.SERIAL, status=config.get_config('status'), status_normal=config.STATUS_NORMAL, status_warn=config.STATUS_WARN, status_error=config.STATUS_ERROR, status_criti=config.STATUS_CRITI)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash('이미 로그인되어 있습니다.', 'warning')
        return render_template('index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                        client_name=session.get('username')), 200
    
    if request.method == 'POST':
        _input_id = request.form.get('userid')
        _input_pw = request.form.get('userpw')
        
        if not _input_id or not _input_pw:
            flash("로그인 실패: 아이디와 비밀번호를 입력해주세요.", "error")
            return render_template('login.html', client_ip=utils.get_client_ip(request)), 401

        # (NAME, LEVEL)
        login_rst = check_login(_input_id, _input_pw)
        if login_rst != False:
            if (login_rst[1] in [0, 1]) == False:
                flash("로그인 실패: 권한이 없습니다.", "error")
                return render_template('login.html', client_ip=utils.get_client_ip(request)), 401
            
            session['userid'] = _input_id
            session['username'] = login_rst[0]
            session['userlevel'] = login_rst[1]
            
            flash(f"({session.get('userid')}) 로그인되었습니다.", 'success')
            return render_template('index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                                    client_name=session.get('username')), 200
        else:
            flash("로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.", "error")
            return render_template('login.html', client_ip=utils.get_client_ip(request)), 401

    return render_template('login.html', client_ip=utils.get_client_ip(request))

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    flash(f"({session.get('userid')}) 로그아웃되었습니다.", 'warning')
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userlevel', None)
    return redirect(url_for('login'), 302)

@app.route("/buzz", methods=["GET"])
@login_required
def buzz():
    if config.get_config('status') == config.STATUS_ERROR:
        flash("경보기가 이미 작동 중입니다.")
        return redirect("/")
    
    threading.Thread(target=_buzz_target, daemon=True).start()
    flash("경보기를 작동했습니다.")
    return redirect("/")

@app.route("/buzz_off", methods=["GET"])
@login_required
def buzz_off():
    config.set_config('status', config.STATUS_NORMAL)
    GPIO.output(config.PIN_BUZZ, GPIO.LOW)
    logger.info("경보기가 해제되었습니다.")
    
    return redirect("/")

@app.route("/reboot", methods=["GET"])
@login_required
def reboot():
    reboot_status = True
    detail = ""
    if config.get_config('status') == config.STATUS_WARN:
        reboot_status = False
        detail = "경보기가 작동 중일 때는 재부팅할 수 없습니다."
        return render_template("reboot.html", reboot_status=reboot_status, detail=detail)
    elif config.get_config('reboot_poss') == False:
        reboot_status = False
        detail = "재부팅이 비활성화 되어있습니다. 재부팅할 수 없습니다."
        return render_template("reboot.html", reboot_status=reboot_status, detail=detail)
    
    if reboot_status == True:
        threading.Thread(target=_reboot_target, daemon=True).start()
        detail = "재부팅이 승인되었습니다."
    
    return render_template("reboot.html", reboot_status=reboot_status, detail=detail)

@app.route("/last_capture", methods=["GET"])
@login_required
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