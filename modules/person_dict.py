import time
import os
import hashlib
import cv2
import numpy as np
from modules.logging import logger
from openvino.runtime import Core

class HumanDetection:
    '''
    detection_model: face-detection-adas-0001\n
    reid_model: face-reidentification-retail-0095
    '''
    def __init__(self, detection_model_path: str, reid_model_path: str, device: str = "CPU"):
        self.core = Core()
        self.detection_model = self.load_model(detection_model_path, device)
        self.reid_model = self.load_model(reid_model_path, device)
        self.detection_input_shape = self.detection_model.inputs[0].shape
        self.reid_input_shape = self.reid_model.inputs[0].shape

    def load_model(self, model_path: str, device: str):
        model = self.core.read_model(f"{model_path}.xml", f"{model_path}.bin")
        compiled_model = self.core.compile_model(model, device)
        return compiled_model

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to load image: {image_path}")
        
        image = cv2.resize(image, (self.detection_input_shape[3], self.detection_input_shape[2]))
        image = image.transpose(2, 0, 1)  # HWC to CHW
        image = image.reshape(1, *image.shape)
        return image

    def extract_face(self, image, detection_threshold=0.5):
        detections = self.detection_model.infer_new_request({0: image})[self.detection_model.outputs[0]]
        
        for detection in detections[0][0]:
            confidence = detection[2]
            if confidence > detection_threshold:
                xmin = int(detection[3] * image.shape[3])
                ymin = int(detection[4] * image.shape[2])
                xmax = int(detection[5] * image.shape[3])
                ymax = int(detection[6] * image.shape[2])
                bbox = [xmin, ymin, xmax, ymax]
                face = image[0, :, ymin:ymax, xmin:xmax]

                if face is None or face.size == 0:
                    continue
                
                face = cv2.resize(face.transpose(1, 2, 0), (self.reid_input_shape[3], self.reid_input_shape[2]))
                return face.transpose(2, 0, 1).reshape(1, 3, self.reid_input_shape[2], self.reid_input_shape[3]), bbox
        
        return None

    def calculate_similarity(self, base_face_embedding, input_face_embedding):
        # Thank you gpt...!!!
        base_norm = np.linalg.norm(base_face_embedding)
        input_norm = np.linalg.norm(input_face_embedding)
        similarity = np.dot(base_face_embedding, input_face_embedding) / (base_norm * input_norm)
        return similarity

    def compare_faces(self, base_face_path, input_face_path):
        # 전처리
        base_image = self.preprocess_image(base_face_path)
        input_image = self.preprocess_image(input_face_path)
        
        # 얼굴 추출
        base_face = self.extract_face(base_image)[0]
        input_face = self.extract_face(input_image)[0]

        if base_face is None or input_face is None:
            return "Could not detect one or both faces."

        # 얼굴 임베딩 추출
        base_face_embedding = self.reid_model.infer_new_request({0: base_face})[self.reid_model.outputs[0]]
        input_face_embedding = self.reid_model.infer_new_request({0: input_face})[self.reid_model.outputs[0]]

        # 유사도 계산
        similarity = self.calculate_similarity(base_face_embedding.flatten(), input_face_embedding.flatten())
        return similarity

    def is_face(self, image_path, detection_threshold=0.5):
        image = self.preprocess_image(image_path)
        face = self.extract_face(image, detection_threshold)
        
        if face == None:
            return False, None
        return True, face[1]
