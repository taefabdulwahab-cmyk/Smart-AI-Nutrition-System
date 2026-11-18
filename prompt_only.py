from gemini_client import generate
def generate_recipe(
    ingredients,
    allergies,
    diabetes=False,
    hypertension=False,
    carb_limit=None,
    sodium_limit=None
):
    """
    Generate one single-serving recipe using Prompt-only.

    Ingredient quantities are returned as:
    - quantity_g: actual ingredient weight in grams
    - display_quantity: human-readable quantity

    Nutritional validation is handled separately.
    """

    return generate(
        ingredients=ingredients,
        allergies=allergies,
        diabetes=diabetes,
        hypertension=hypertension,
        carb_limit=carb_limit,
        sodium_limit=sodium_limit
    )
