from gemini_client import generate
from retrieval import retrieve_guidelines

def generate_rag_recipe(ingredients, allergies, diabetes=False, hypertension=False,
                        carb_limit=None, sodium_limit=None):
    guidelines = retrieve_guidelines(allergies, diabetes, hypertension)
    return generate(ingredients, allergies, diabetes, hypertension,
                    carb_limit, sodium_limit, guidelines=guidelines)
