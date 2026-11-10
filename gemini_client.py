
import os
import json
from google import genai
from google.genai import types
from config import MODEL

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "recipe_name": {"type": "STRING"},
        "ingredients": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "quantity_g": {"type": "NUMBER"}
                },
                "required": ["name", "quantity_g"]
            }
        },
        "steps": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "message": {"type": "STRING"}
    },
    "required": [
        "recipe_name",
        "ingredients",
        "steps",
        "message"
    ]
}


def generate(
    ingredients,
    allergies,
    diabetes=False,
    hypertension=False,
    carb_limit=None,
    sodium_limit=None,
    guidelines=None
):
    key = os.getenv("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY missing. Add it to your .env file."
        )

    if not ingredients:
        raise ValueError("No detected ingredients supplied")

    # Same base instructions for Prompt-only and RAG.
    prompt = f"""
Create ONE single-serving recipe using ONLY these available food ingredients:

{json.dumps(ingredients, ensure_ascii=False)}

User dietary restrictions:
- Allergies: {json.dumps(allergies, ensure_ascii=False)}
- Diabetes: {diabetes}
- Hypertension: {hypertension}
- Maximum carbohydrates per serving (g): {carb_limit if diabetes else 'not applicable'}
- Maximum sodium per serving (mg): {sodium_limit if hypertension else 'not applicable'}

IMPORTANT INGREDIENT RULES:
1. Use ONLY ingredients from the available ingredients list.
2. Copy ingredient names EXACTLY as provided.
3. Do not add prefixes, suffixes, or descriptions to ingredient names.
4. Do not substitute or rename ingredients.
5. Do not introduce ingredients that are not available.
6. Exclude every listed allergen.
7. If an available ingredient conflicts with an allergy, do not use it.
8. Each ingredient must have a numeric quantity_g in grams.
9. Do not rename ingredients to claim they are allergen-free.
10. Water for cooking is allowed.
11. Do not introduce salt, oil, or sauces unless listed.
12. Use realistic quantities for ONE serving.
13. Use raw/uncooked ingredient weights unless explicitly stated otherwise.
14. Explain the weight basis in the message.
15. Provide clear preparation steps.
16. Try to meet active carbohydrate and sodium limits.
17. Do not claim that the recipe has been independently validated.
18. If no valid recipe is feasible, return an empty ingredients array and explain why in message.

OUTPUT REQUIREMENTS:
- Return one recipe in JSON format.
- Include recipe_name, ingredients, steps, and message.
- Every ingredient name must match an available ingredient exactly.
- Do not include additional ingredient descriptions in the name field.
"""

    # Only RAG receives retrieved dietary guidelines.
    if guidelines:
        prompt += (
            "\nRelevant retrieved dietary guidelines "
            "(additional RAG context):\n"
            + "\n".join(
                f"- {g['guideline']} "
                f"(Source: {g['source']}; {g['url']})"
                for g in guidelines
            )
        )

    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=SCHEMA
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    recipe = json.loads(response.text)

    # Check that generated ingredients are allowed.
    allowed = {
        x.casefold().strip()
        for x in ingredients
    }

    for item in recipe.get("ingredients", []):
        name = item["name"].casefold().strip()

        if name not in allowed:
            raise ValueError(
                f"Generated ingredient not in available list: {item['name']}"
            )

        quantity = item["quantity_g"]

        if (
            not isinstance(quantity, (int, float))
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise ValueError(
                "Ingredient weights must be positive numbers"
            )

    return recipe

