"""Offline checks for the exported recipe handoff; does not call Gemini or change Jumana's files."""
import csv
import json
from pathlib import Path
from config import CARB_LIMIT_G, SODIUM_LIMIT_MG

ROOT = Path(__file__).resolve().parent
RECIPES = ROOT / 'recipes_for_validation.json'
CSV_PATH = ROOT / 'jumana_original_reference' / 'ingredients_nutrition_allergen_review.csv'


def main():
    if not RECIPES.exists():
        raise SystemExit('Run python run_tests.py then python export_recipes.py first.')
    recipes = json.loads(RECIPES.read_text(encoding='utf-8'))
    if not isinstance(recipes, list):
        raise ValueError('Expected a JSON list of recipes')
    keys = set()
    for recipe in recipes:
        key = (recipe['test_case_id'], recipe['method'])
        if key in keys:
            raise ValueError(f'Duplicate case/method: {key}')
        keys.add(key)
        if recipe['method'] not in ('prompt_only', 'rag_assisted'):
            raise ValueError(f'Unknown method: {key}')
        expected_carb = CARB_LIMIT_G if recipe.get('diabetes') else None
        expected_sodium = SODIUM_LIMIT_MG if recipe.get('hypertension') else None
        if recipe.get('carb_limit') != expected_carb or recipe.get('sodium_limit') != expected_sodium:
            raise ValueError(f'Wrong limits for {key}')
        if not recipe.get('ingredients'):
            print(f'WARNING {key}: empty ingredient list, not verifiable')
        for ingredient in recipe.get('ingredients', []):
            if not isinstance(ingredient.get('quantity_g'), (int, float)) or ingredient['quantity_g'] <= 0:
                raise ValueError(f'Invalid weight for {key}: {ingredient}')
    print(f'Export structure OK: {len(recipes)} recipes across {len({k[0] for k in keys})} cases.')
    if CSV_PATH.exists():
        with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f'Jumana CSV reference: {len(rows)} rows; headers: {reader.fieldnames}')
    print('This is a format check only, NOT nutritional or allergy validation.')


if __name__ == '__main__':
    main()
