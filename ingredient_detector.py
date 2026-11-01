from ultralytics import YOLO
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "Colab-best_food_ingredients.pt"

model = YOLO(str(MODEL_PATH))

def detect_ingredients(image):
    results = model.predict(
        source=image,
        conf=0.30,
        verbose=False
    )

    detections = []

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()

        detections.append({
            "name": model.names[class_id],
            "confidence": confidence,
            "bounding_box": coordinates
        })

    annotated_image = results[0].plot()

    return detections, annotated_image