# Smart-AI-Nutrition-System

Smart AI Nutrition System

1. Project Overview

Smart AI Nutrition System is an AI-based prototype designed to identify raw food ingredients from images and support personalized recipe generation.

The system aims to combine computer vision, Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and nutritional validation.

The system considers user-provided dietary information, including:

- Food allergies.
- Diabetes.
- Hypertension.
- Dietary preferences and nutritional limits.

This project is an educational prototype and is not intended to replace professional medical or nutritional advice.

2. Project Structure

Smart AI Nutrition System/
│
├── app.py
├── ingredient_detector.py
├── Colab-best_food_ingredients.pt
├── test_detector.py
├── main.py
├── nutrition_validator.py
├── recipe_generator.py
├── rag.py
├── recipes_for_validation.json
├── all_results.json
├── README.md
├── requirements.txt
│
├── data/
│ ├── ingredients_nutrition_allergen_review.csv
│ └── test_cases.csv
│
└── Test-images/
└── egg+bnana.png

3. Main Components

Ingredient Detection

- Uses a trained YOLOv8 model.
- Detects food ingredients from uploaded images.
- Returns ingredient names, confidence scores, and bounding boxes.
- Uses "ingredient_detector.py" to load the trained model.

Recipe Generation

- Uses an LLM to generate recipes based on detected ingredients and user information.
- Implemented in "recipe_generator.py".

Retrieval-Augmented Generation (RAG)

- Supports recipe generation using retrieved dietary information and guidelines.
- Implemented in "rag.py".

Nutrition Validation

- Uses nutritional information stored in a CSV dataset.
- Estimates nutritional values based on ingredient quantities.
- Checks nutritional constraints and identifies potential allergy matches.
- Implemented in "nutrition_validator.py" and "main.py".

4. Dataset and Nutritional Information

The project uses:

- A food ingredient detection dataset containing 36 ingredient classes.
- "ingredients_nutrition_allergen_review.csv" for nutritional and allergen-related information.
- "test_cases.csv" for test case information.

Nutritional calculations follow these assumptions:

- Ingredient quantities are provided in grams.
- Dataset nutritional values are expected per 100 grams.
- Missing nutritional information should not be treated as zero.
- Missing data may result in an UNKNOWN validation status.
- Approximate nutritional values should be identified as estimates.

5. Allergy and Nutrition Limitations

The current allergy-checking implementation has limited coverage and checks egg and banana only.

An allergy warning may appear when:

- An allergen is detected as a direct ingredient.
- The dataset explicitly identifies an ingredient as containing an allergen.

The absence of an allergy warning does not prove that a recipe is allergen-free.

Composite products such as mayonnaise, pasta, sausages, and dumplings may require additional ingredient-label verification.

Nutritional limits used in the current validation code are demonstration values only and are not medical recommendations.

6. Testing

Test Ingredient Detection

Make sure the trained model file and test image are available.

Open a terminal in the project directory and run:

python test_detector.py

The test displays:

- Detected ingredient names.
- Confidence scores.
- Bounding box coordinates.
- An annotated image showing detected ingredients.

Test Nutrition Validation

The nutrition validation component is tested through "main.py".

The test recipes are stored in:

recipes_for_validation.json

Run:

python main.py

Note: The current testing scripts are separate component tests and do not represent the complete integrated application.

7. Current Development Status

Component| Status
YOLO ingredient detection| Implemented and tested
Nutrition CSV loading| Implemented
Nutrition validation| Under development
Recipe generation| Pending implementation
RAG integration| Pending implementation
Streamlit interface| Pending implementation
Full system integration| Pending implementation

8. Important Notes

- Keep the project folder structure unchanged.
- Ensure the trained ".pt" model file is available in the main project directory.
- Keep the nutritional CSV file inside the "data" folder.
- Install the required Python libraries before running the project.
- The project is still under development, and individual components must be tested before full integration.
