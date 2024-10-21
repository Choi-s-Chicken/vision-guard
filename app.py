import os
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