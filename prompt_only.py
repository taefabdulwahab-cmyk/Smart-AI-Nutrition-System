from gemini_client import generate

def generate_recipe(ingredients, allergies, diabetes=False, hypertension=False,
                    carb_limit=None, sodium_limit=None):
    return generate(ingredients, allergies, diabetes, hypertension, carb_limit, sodium_limit)
