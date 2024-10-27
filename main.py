import os
import time
import cv2
import threading
import config
import src.utils as utils
from modules.logging import logger
from modules.person_dict import HumanDetection

def _capture_target(_capture_delay):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("카메라를 열 수 없습니다.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("프레임을 가져올 수 없습니다.")
                continue
            
            save_name = f'{utils.get_now_ftime()}.jpg'
            cv2.imwrite(os.path.join(config.CAPTURE_FOLDER_PATH, save_name), frame)
            logger.info(f"{save_name} 캡쳐 완료")
            time.sleep(_capture_delay)

    cap.release()
threading.Thread(target=_capture_target, args=(1,), daemon=True).start()



time.sleep(10)