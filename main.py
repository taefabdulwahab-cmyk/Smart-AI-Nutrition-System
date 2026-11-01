
import json
from pathlib import Path

from nutrition_validator import (
    NutritionValidator,
    IngredientAmount,
    number_from_cell,
    normalize_name,
    normalize_column
)


# ==========================================
# Experimental Project Thresholds
# ==========================================

SUGAR_LIMIT = 10          # g per recipe
CARBS_LIMIT = 45          # g per recipe
SODIUM_LIMIT = 600       # mg per recipe

RECIPES_FILE = Path(__file__).with_name(
    "recipes_for_validation.json"
)


# ==========================================
# CSV Field Helpers
# ==========================================

def get_field(row, possible_names):
    """Find a field using alternative column names."""

    normalized_row = {
        normalize_column(key): value
        for key, value in row.items()
    }

    for name in possible_names:
        key = normalize_column(name)

        if key in normalized_row:
            return normalized_row[key]

    return None


# ==========================================
# Allergy Warnings
# ==========================================

def is_positive(value):
    """Interpret common positive CSV values."""

    return str(value or "").strip().lower() in {
        "yes", "true", "1", "contains", "present"
    }


def get_allergy_warnings(name, row, allergies):

    warnings = []

    name = normalize_name(name)

    allergies = {
        normalize_name(allergy)
        for allergy in allergies
    }

    # Egg allergy
    if "egg" in allergies:

        egg_status = None

        if row is not None:
            egg_status = get_field(
                row,
                [
                    "egg_allergy_status",
                    "contains_egg",
                    "egg",
                    "egg_allergen"
                ]
            )

        egg_match = (
            "egg" in name
            or is_positive(egg_status)
        )

        if egg_match:
            warnings.append(
                "Egg Allergy Warning: "
                "This ingredient may contain egg."
            )

    # Banana allergy
    if "banana" in allergies:

        banana_status = None

        if row is not None:
            banana_status = get_field(
                row,
                [
                    "banana_allergy_status",
                    "contains_banana",
                    "banana",
                    "banana_allergen"
                ]
            )

        banana_match = (
            "banana" in name
            or is_positive(banana_status)
        )

        if banana_match:
            warnings.append(
                "Banana Allergy Warning: "
                "This ingredient may contain banana."
            )

    # General allergen record
    # Do not assign this field to a specific allergen
    # unless its meaning is known.
    if row is not None:

        general_status = get_field(
            row,
            [
                "allergen_egg_banana"
            ]
        )

        if is_positive(general_status):

            if not warnings:
                warnings.append(
                    "Allergen Warning: "
                    "Check the recorded allergen information."
                )

    return warnings


# ==========================================
# Print Recipe
# ==========================================

def print_recipe(recipe, validator):

    test_case_id = recipe.get(
        "test_case_id", "Unknown"
    )

    method = recipe.get(
        "method", "Unknown"
    )

    recipe_name = recipe.get(
        "recipe_name", "Unknown"
    )

    allergies = recipe.get("allergies", [])

    ingredients = []

    # Create IngredientAmount objects
    for item in recipe.get("ingredients", []):

        amount = IngredientAmount(
            name=str(item["name"]),
            grams=float(item["quantity_g"])
        )

        ingredients.append(amount)

    # Total weight
    total_weight = sum(
        item.grams for item in ingredients
    )

    # Nutrition totals
    total_carbs = 0.0
    total_sugar = 0.0
    total_sodium = 0.0

    unknown_carbs = []
    unknown_sugar = []
    unknown_sodium = []

    allergy_warnings = []

    # ======================================
    # Recipe Information
    # ======================================

    print("\n" + "=" * 55)

    print("TEST CASE:", test_case_id)
    print("METHOD:", method)
    print("RECIPE:", recipe_name)

    print(f"Total Recipe Weight: {total_weight:.2f} g")

    print("=" * 55)

    print("\nINGREDIENT DETAILS:")

    # ======================================
    # Process Ingredients
    # ======================================

    for item in ingredients:

        name = item.name
        grams = item.grams

        print("\n" + "-" * 40)

        print("Ingredient:", name)
        print(f"Weight: {grams:.2f} g")

        # Invalid weight
        if grams <= 0:

            print("Invalid ingredient weight.")

            unknown_carbs.append(name)
            unknown_sugar.append(name)
            unknown_sodium.append(name)

            continue

        # Find ingredient in CSV
        key = normalize_name(name)
        row = validator.items.get(key)

        if row is None:

            print("Nutrition data: UNAVAILABLE")

            unknown_carbs.append(name)
            unknown_sugar.append(name)
            unknown_sodium.append(name)

            warnings = get_allergy_warnings(
                name, None, allergies
            )

            for warning in warnings:
                print(warning)
                allergy_warnings.append(warning)

            continue

        # ----------------------------------
        # Read nutrition values per 100 g
        # ----------------------------------

        carbs_100g = number_from_cell(
            get_field(
                row,
                [
                    "carbohydrates_g_per_100g",
                    "carbs_g_per_100g",
                    "carbohydrates",
                    "carbs"
                ]
            )
        )

        sugar_100g = number_from_cell(
            get_field(
                row,
                [
                    "sugar_g_per_100g",
                    "total_sugars_g_per_100g",
                    "sugars_g_per_100g",
                    "sugar",
                    "sugars"
                ]
            )
        )

        sodium_100g = number_from_cell(
            get_field(
                row,
                [
                    "sodium_mg_per_100g",
                    "sodium_mg",
                    "sodium"
                ]
            )
        )

        # Convert ingredient quantity to nutrition
        factor = grams / 100.0

        carbs = (
            carbs_100g * factor
            if carbs_100g is not None
            else None
        )

        sugar = (
            sugar_100g * factor
            if sugar_100g is not None
            else None
        )

        sodium = (
            sodium_100g * factor
            if sodium_100g is not None
            else None
        )

        # ----------------------------------
        # Display & Accumulate Carbohydrates
        # ----------------------------------

        if carbs is not None:

            print(f"Carbohydrates: {carbs:.2f} g")
            total_carbs += carbs

        else:

            print("Carbohydrates: UNAVAILABLE")
            unknown_carbs.append(name)

        # ----------------------------------
        # Display & Accumulate Sugar
        # ----------------------------------

        if sugar is not None:

            print(f"Sugar: {sugar:.2f} g")
            total_sugar += sugar

        else:

            print("Sugar: UNAVAILABLE")
            unknown_sugar.append(name)

        # ----------------------------------
        # Display & Accumulate Sodium
        # ----------------------------------

        if sodium is not None:

            print(f"Sodium: {sodium:.2f} mg")
            total_sodium += sodium

        else:

            print("Sodium: UNAVAILABLE")
            unknown_sodium.append(name)

        # ----------------------------------
        # Allergy Check
        # ----------------------------------

        warnings = get_allergy_warnings(
            name, row, allergies
        )

        if warnings:

            for warning in warnings:

                print(warning)
                allergy_warnings.append(warning)

        else:

            print(
                "No recorded match found for "
                "specified allergies."
            )

    # ======================================
    # Total Nutrition
    # ======================================

    print("\n" + "=" * 55)
    print("TOTAL NUTRITION")
    print("=" * 55)

    print(f"Total Recipe Weight: {total_weight:.2f} g")

    if unknown_carbs:

        print(
            f"Known Carbohydrates (PARTIAL): "
            f"{total_carbs:.2f} g"
        )

    else:

        print(
            f"Total Carbohydrates: "
            f"{total_carbs:.2f} g"
        )

    if unknown_sugar:

        print(
            f"Known Sugar (PARTIAL): "
            f"{total_sugar:.2f} g"
        )

    else:

        print(f"Total Sugar: {total_sugar:.2f} g")

    if unknown_sodium:

        print(
            f"Known Sodium (PARTIAL): "
            f"{total_sodium:.2f} mg"
        )

    else:

        print(f"Total Sodium: {total_sodium:.2f} mg")

    # ======================================
    # Nutrition Data Status
    # ======================================

    nutrition_complete = (
        not unknown_carbs
        and not unknown_sugar
        and not unknown_sodium
    )

    if nutrition_complete:
        print("Nutrition Data Status: COMPLETE")
    else:
        print("Nutrition Data Status: INCOMPLETE")

    # ======================================
    # Nutrition Classification
    # ======================================

    print("\nNUTRITION CLASSIFICATION")
    print("-" * 55)

    # Sugar
    if not unknown_sugar:

        if total_sugar >= SUGAR_LIMIT:
            print("Sugar: HIGH")
        else:
            print("Sugar: LOW")

    else:
        print("Sugar: INCOMPLETE")

    # Carbohydrates
    if not unknown_carbs:

        if total_carbs >= CARBS_LIMIT:
            print("Carbohydrates: HIGH")
        else:
            print("Carbohydrates: LOW")

    else:
        print("Carbohydrates: INCOMPLETE")

    # Sodium
    if not unknown_sodium:

        if total_sodium >= SODIUM_LIMIT:
            print("Sodium: HIGH")
        else:
            print("Sodium: LOW")

    else:
        print("Sodium: INCOMPLETE")

    # ======================================
    # Allergy Summary
    # ======================================

    print("\nALLERGY SUMMARY")
    print("-" * 55)

    if allergy_warnings:

        for warning in dict.fromkeys(allergy_warnings):
            print(warning)

    else:

        print(
            "No recorded match found for "
            "specified allergies."
        )

    print(
        "This does not guarantee allergen safety."
    )

    print("=" * 55)


# ==========================================
# Main
# ==========================================

def main():

    try:

        validator = NutritionValidator()

        if not RECIPES_FILE.exists():

            print(
                "Error: recipes_for_validation.json "
                "not found."
            )

            return

        with open(
            RECIPES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            recipes = json.load(file)

        # Support list or {"recipes": [...]}
        if isinstance(recipes, dict):
            recipes = recipes.get("recipes", [])

        if not recipes:
            print("No recipes found.")
            return

        print(f"Number of recipes: {len(recipes)}")

        for recipe in recipes:
            print_recipe(recipe, validator)

        print("\nFinished processing all recipes.")

    except (FileNotFoundError, ValueError, KeyError) as error:

        print("Error:", error)


if __name__ == "__main__":
    main()
