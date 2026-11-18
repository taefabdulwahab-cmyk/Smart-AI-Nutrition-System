from gemini_client import generate
from retrieval import retrieve_guidelines
def generate_rag_recipe(
    ingredients,
    allergies,
    diabetes=False,
    hypertension=False,
    carb_limit=None,
    sodium_limit=None
):
    """
    Generate one single-serving recipe using RAG.

    Retrieves relevant dietary guidelines before
    generating the recipe.

    Each generated ingredient includes:
    - quantity_g: ingredient weight in grams
    - display_quantity: human-readable quantity

    Nutritional validation is handled separately.
    """

    guidelines = retrieve_guidelines(
        allergies,
        diabetes,
        hypertension
    )

    return generate(
        ingredients=ingredients,
        allergies=allergies,
        diabetes=diabetes,
        hypertension=hypertension,
        carb_limit=carb_limit,
        sodium_limit=sodium_limit,
        guidelines=guidelines
    )
