import cv2
import numpy as np
from openvino.runtime import Core

MODEL_PATH = "model/person-detection-0303/FP16/person-detection-0303.xml"

def load_model(model_path, device="CPU"):
    ie = Core()
    model = ie.read_model(model=model_path)
    compiled_model = ie.compile_model(model=model, device_name=device)
    return compiled_model

def preprocess_frame(frame, input_shape):
    resized_frame = cv2.resize(frame, (input_shape[3], input_shape[2]))
    processed_frame = resized_frame.transpose(2, 0, 1)  # HWC -> CHW
    processed_frame = np.expand_dims(processed_frame, axis=0)
    return processed_frame

def run_inference(compiled_model, input_blob, frame):
    input_shape = compiled_model.input(index=0).shape
    preprocessed_frame = preprocess_frame(frame, input_shape)
    
    results = compiled_model([preprocessed_frame])[compiled_model.output(index=0)]
    return results

def draw_results(frame, results, threshold=0.5):
    h, w = frame.shape[:2]
    for result in results:
        conf = result[4]
        if conf > threshold:
            xmin = int(result[0])
            ymin = int(result[1])
            xmax = int(result[2])
            ymax = int(result[3])

            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            print(f"DETECTED: {conf} | {result}")
        else:
            print(f"Low: {conf} | {result}")
    return frame

def main():
    cap = cv2.VideoCapture(0)

    compiled_model = load_model(MODEL_PATH)
    input_blob = compiled_model.input(index=0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = run_inference(compiled_model, input_blob, frame)
        output_frame = draw_results(frame, results)

        cv2.imshow("Person Detection (FP32)", output_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
