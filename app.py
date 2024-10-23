import os
import time
import subprocess
import requests
from dotenv import load_dotenv
import threading
import src.utils as utils

load_dotenv(verbose=True)
PROCESS_URL = os.getenv("PROCESS_URL")

class Main:
    def __init__(self):
        self.load_option()

    def load_option(self):
        self.OPTION = utils.get_option()

def capture_and_send():
    # 사진 찍기 (해상도 조정)
    capture_cmd = ["libcamera-jpeg", "-o", "frame.jpg", "--nopreview", "--width", "640", "--height", "480"]
    subprocess.run(capture_cmd)
    
    # 찍은 사진을 API로 전송
    print(f"{utils.get_now_ftime()} Requesting . . .")
    with open("frame.jpg", "rb") as image_file:
        requests.post(f"{PROCESS_URL}/image", files={"file": image_file})
    print(f"{utils.get_now_ftime()} Requested.")

if __name__ == '__main__':
    main = Main()
    
    # 첫 번째 더미 사진 찍기 (워밍업)
    subprocess.run(["libcamera-jpeg", "-o", "/dev/null", "--nopreview"])
    
    while True:
        # 병렬로 사진 찍고 보내기
        capture_thread = threading.Thread(target=capture_and_send)
        capture_thread.start()
        
        # 일정 시간 대기 (1초)
        time.sleep(1)
