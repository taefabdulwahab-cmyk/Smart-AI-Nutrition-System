import json
from pathlib import Path

from nutrition_validator import (
    NutritionValidator,
    IngredientAmount,
    number_from_cell,
    normalize_name,
    normalize_column
)


SUGAR_LIMIT = 10
CARBS_LIMIT = 45
SODIUM_LIMIT = 600


def get_field(row, *names):
    for name in names:
        key = normalize_column(name)
        value = row.get(key)

        if value is not None and str(value).strip() != "":
            return number_from_cell(value)

    return None


def get_allergy_warnings(name, allergies):
    warnings = []

    ingredient = normalize_name(name)

    allergies = [
        normalize_name(item)
        for item in allergies
    ]

    if "egg" in allergies and ingredient == "egg":
        warnings.append(
            "Warning: Recipe contains egg, which matches the user's allergy."
        )

    if "banana" in allergies and ingredient == "banana":
        warnings.append(
            "Warning: Recipe contains banana, which matches the user's allergy."
        )

    return warnings


def print_recipe(recipe, validator):

    test_id = recipe.get("test_case_id", "Unknown")
    method = recipe.get("method", "Unknown")
    recipe_name = recipe.get("recipe_name", "Unnamed Recipe")
    allergies = recipe.get("allergies", [])

    ingredients = recipe.get("ingredients", [])

    total_weight = 0
    total_carbs = 0
    total_sugar = 0
    total_sodium = 0

    nutrition_complete = True
    allergy_summary = []

    print("\n" + "=" * 55)
    print("TEST CASE:", test_id)
    print("METHOD:", method)
    print("RECIPE:", recipe_name)

    print("=" * 55)

    print("\nINGREDIENT DETAILS:")

    for ingredient in ingredients:

        name = normalize_name(ingredient.get("name", ""))
        grams = number_from_cell(
            ingredient.get("quantity_g")
        )

        if grams is None:
            grams = 0

        total_weight += grams

        row = validator.items.get(name)

        print("\n" + "-" * 40)
        print("Ingredient:", name)
        print(f"Weight: {grams:.2f} g")

        if row is None:
            print("Nutrition Data: Not available")
            nutrition_complete = False
            continue

        carbs_per_100g = get_field(
            row, "carbohydrates_g_per_100g"
        )

        sugar_per_100g = get_field(
            row, "sugar_g_per_100g"
        )

        sodium_per_100g = get_field(
            row, "sodium_mg_per_100g"
        )

        if (
            carbs_per_100g is None
            or sugar_per_100g is None
            or sodium_per_100g is None
        ):
            nutrition_complete = False

        carbs = (
            carbs_per_100g * grams / 100
            if carbs_per_100g is not None else 0
        )

        sugar = (
            sugar_per_100g * grams / 100
            if sugar_per_100g is not None else 0
        )

        sodium = (
            sodium_per_100g * grams / 100
            if sodium_per_100g is not None else 0
        )

        total_carbs += carbs
        total_sugar += sugar
        total_sodium += sodium

        print(f"Carbohydrates: {carbs:.2f} g")
        print(f"Sugar: {sugar:.2f} g")
        print(f"Sodium: {sodium:.2f} mg")

        warnings = get_allergy_warnings(
            name, allergies
        )

        for warning in warnings:
            print(warning)
            allergy_summary.append(warning)

    print("\n" + "=" * 55)
    print("TOTAL NUTRITION")
    print("=" * 55)

    print(f"Total Recipe Weight: {total_weight:.2f} g")
    print(f"Total Carbohydrates: {total_carbs:.2f} g")
    print(f"Total Sugar: {total_sugar:.2f} g")
    print(f"Total Sodium: {total_sodium:.2f} mg")

    status = "COMPLETE" if nutrition_complete else "INCOMPLETE"
    print("Nutrition Data Status:", status)

    print("\nNUTRITION CLASSIFICATION")
    print("-" * 55)

    print(
        "Sugar:",
        "LOW" if total_sugar <= SUGAR_LIMIT else "HIGH"
    )

    print(
        "Carbohydrates:",
        "LOW" if total_carbs <= CARBS_LIMIT else "HIGH"
    )

    print(
        "Sodium:",
        "LOW" if total_sodium <= SODIUM_LIMIT else "HIGH"
    )

    print("\nALLERGY SUMMARY")
    print("-" * 55)

    if allergy_summary:
        for warning in allergy_summary:
            print(warning)
    else:
        print("No matching egg or banana ingredient found.")

    print("=" * 55)


def main():

    try:
        validator = NutritionValidator()

        results_file = Path(__file__).with_name(
            "all_results (2).json"
        )

        if not results_file.exists():
            print("Error: all_results (2).json not found.")
            return

        with open(
            results_file,
            "r",
            encoding="utf-8"
        ) as file:
            test_cases = json.load(file)

        print(f"Number of test cases: {len(test_cases)}")

        total_recipes = 0

        for case in test_cases:

            test_info = case.get("test_case", {})

            test_id = test_info.get("id", "Unknown")
            allergies = test_info.get("allergies", [])

            print("\n")
            print("#" * 65)
            print("TEST CASE:", test_id)
            print("Allergies:", allergies)
            print("#" * 65)

            for method in ["prompt_only", "rag_assisted"]:

                recipe = case.get(method)

                if not recipe:
                    continue

                recipe_data = recipe.copy()

                recipe_data["test_case_id"] = test_id
                recipe_data["method"] = method
                recipe_data["allergies"] = allergies

                print_recipe(recipe_data, validator)

                total_recipes += 1

        print("\n" + "=" * 55)
        print("VALIDATION SUMMARY")
        print("=" * 55)
        print(f"Number of recipes validated: {total_recipes}")
        print("Finished validating available recipes.")

    except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
        print("Error:", error)


if __name__ == "__main__":
    main()