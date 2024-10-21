import cv2
import numpy as np
from openvino.runtime import Core

class PersonDetection:
    def __init__(self, human_dtct_model_path: str, device: str = "CPU"):
        self.core = Core()
        self.human_dtct_model = self.load_model(human_dtct_model_path, device)
        self.input_shape = self.human_dtct_model.inputs[0].shape

    def load_model(self, model_path: str, device: str):
        model = self.core.read_model(f"{model_path}.xml", f"{model_path}.bin")
        compiled_model = self.core.compile_model(model, device)
        return compiled_model

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to load image: {image_path}")
        
        image = cv2.resize(image, (self.input_shape[3], self.input_shape[2]))
        image = image.transpose(2, 0, 1)  # HWC to CHW
        image = image.reshape(1, *image.shape)
        return image

    def detect_people(self, image_path, detection_threshold=0.5):
        image = self.preprocess_image(image_path)
        detections = self.human_dtct_model.infer_new_request({0: image})[self.human_dtct_model.outputs[0]]
        
        results = []
        for detection in detections[0][0]:
            confidence = detection[2]
            if confidence > detection_threshold:
                bbox = {
                    'xmin': int(detection[3] * image.shape[3]),
                    'ymin': int(detection[4] * image.shape[2]),
                    'xmax': int(detection[5] * image.shape[3]),
                    'ymax': int(detection[6] * image.shape[2]),
                }
                person_id = int(detection[1])  # Replace with your logic for assigning IDs
                results.append({
                    'bbox': bbox,
                    'confidence': confidence,
                    'person_id': person_id
                })
        
        return results

# 예시 사용법
# model_path = "path/to/your/person-detection-0303"
# detector = PersonDetection(model_path)
# results = detector.detect_people("path/to/your/image.jpg")
# print(results)
