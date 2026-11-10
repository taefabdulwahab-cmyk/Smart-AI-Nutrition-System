import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
source = ROOT / "all_results.json"
if not source.exists():
    raise SystemExit("all_results.json not found. Run run_tests.py first.")
results = json.loads(source.read_text(encoding="utf-8"))
export = []
for row in results:
    case = row["test_case"]
    for method in ("prompt_only", "rag_assisted"):
        recipe = row.get(method)
        if not recipe:
            continue
        export.append({
            "test_case_id": case["id"], "method": method,
            "recipe_name": recipe["recipe_name"],
            "ingredients": recipe["ingredients"],
            "steps": recipe.get("steps", []),
            "allergies": case.get("allergies", []),
            "diabetes": case.get("diabetes", False),
            "hypertension": case.get("hypertension", False),
            "carb_limit": case.get("carb_limit"),
            "sodium_limit": case.get("sodium_limit"),
            "sugar_limit": 10  # Existing Jumana classification only; not a diabetes pass/fail rule
        })
output = ROOT / "recipes_for_validation.json"
output.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Exported {len(export)} recipes to {output.name}")
