import cv2
import numpy as np
from openvino.runtime import Core
from src.sort.sort import Sort

class PersonDetector:
    def __init__(self, model_path, device="CPU"):
        self.ie = Core()
        self.model = self.ie.read_model(model=model_path)
        self.compiled_model = self.ie.compile_model(model=self.model, device_name=device)
        self.infer_request = self.compiled_model.create_infer_request()
        
        self.tracker = Sort()

    def detect_and_track(self, frame):
        input_tensor = np.expand_dims(frame, 0)
        result = self.infer_request.infer({0: input_tensor})
        
        detections = result['detection_output']
        boxes = []
        for detection in detections[0][0]:
            confidence = detection[2]
            if confidence > 0.5:  # 신뢰도 필터링
                x_min, y_min, x_max, y_max = detection[3:7]
                boxes.append([x_min, y_min, x_max, y_max, confidence])
        
        tracked_objects = self.tracker.update(np.array(boxes))
        
        tracked_results = []
        for obj in tracked_objects:
            obj_id = int(obj[4])  # 객체 ID
            x_min, y_min, x_max, y_max = obj[:4]
            tracked_results.append({
                "id": obj_id,
                "bbox": [x_min, y_min, x_max, y_max]
            })
        
        return tracked_results
