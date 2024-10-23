import os

import cv2
import src.utils as utils
from src.face_reco import FaceRecognition
from src.human_dtct import PersonDetection

class Main:
    def __init__(self):
        self.load_option()
        self.FaceRecognition = FaceRecognition(self.FACE_DTCT_PATH, self.FACE_REID_PATH)
        self.PersonDetection = PersonDetection(self.PERSON_DTCT_PATH)
        
    def load_option(self):
        self.OPTION = utils.get_option()
        self.FACE_DTCT_INFO = self.OPTION['face_detection']
        self.FACE_DTCT_PATH = f"{self.FACE_DTCT_INFO['model_path']}/{self.FACE_DTCT_INFO['model_type']}/{self.FACE_DTCT_INFO['model_name']}"
        self.FACE_REID_INFO = self.OPTION['face_reidentification']
        self.FACE_REID_PATH = f"{self.FACE_REID_INFO['model_path']}/{self.FACE_REID_INFO['model_type']}/{self.FACE_REID_INFO['model_name']}"
        self.PERSON_DTCT_INFO = self.OPTION['person_detection']
        self.PERSON_DTCT_PATH = f"{self.PERSON_DTCT_INFO['model_path']}/{self.PERSON_DTCT_INFO['model_type']}/{self.PERSON_DTCT_INFO['model_name']}"


if __name__ == '__main__':
    main = Main()
    
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imwrite("frame.jpg", frame)
        
        face_result = main.FaceRecognition.is_face('frame.jpg')
        if face_result[0] == True:
            cv2.rectangle(frame, (face_result[1][0], face_result[1][1]), (face_result[1][2], face_result[1][3]), (0, 255, 0), 2)
        
        person_result = main.PersonDetection.detect_people('frame.jpg')
        for person in person_result:
            cv2.rectangle(frame, (person['bbox']['xmin'], person['bbox']['ymin']), (person['bbox']['xmax'], person['bbox']['ymax']), (255, 0, 0), 2)
        
        cv2.imshow("Detection Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()