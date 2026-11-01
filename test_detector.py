from ingredient_detector import detect_ingredients
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path

IMAGE_PATH = Path(__file__).parent / "Test-images" / "egg+bnana.png"
image = Image.open(IMAGE_PATH)

detections, annotated_image = detect_ingredients(image)

for item in detections:
    print(f"Ingredient: {item['name']}")
    print(f"Confidence: {item['confidence']:.2%}")
    print(f"Bounding Box: {item['bounding_box']}")
    print("--------------------")

plt.imshow(annotated_image[:, :, ::-1])
plt.axis("off")
plt.show()