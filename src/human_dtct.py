import cv2
import numpy as np
from openvino.runtime import Core

class PersonDetector:
    def __init__(self, model_path, device="CPU"):
        self.ie = Core()
        self.model = self.ie.read_model(model=model_path)
        self.compiled_model = self.ie.compile_model(model=self.model, device_name=device)
        self.infer_request = self.compiled_model.create_infer_request()
        