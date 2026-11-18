
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# Read the new experiment results.
source = ROOT / "all_results_v2.json"

if not source.exists():
    raise SystemExit(
        "all_results_v2.json not found. "
        "Run run_tests.py first."
    )

results = json.loads(
    source.read_text(encoding="utf-8")
)

export = []

for row in results:
    case = row["test_case"]

    for method in ("prompt_only", "rag_assisted"):
        recipe = row.get(method)

        if not recipe:
            continue

        export.append({
            "test_case_id": case["id"],
            "method": method,
            "recipe_name": recipe["recipe_name"],

            # Preserve actual ingredient weights and
            # human-readable quantities for each ingredient.
            "ingredients": recipe["ingredients"],

            "steps": recipe.get("steps", []),
            "allergies": case.get("allergies", []),
            "diabetes": case.get("diabetes", False),
            "hypertension": case.get("hypertension", False),
            "carb_limit": case.get("carb_limit"),
            "sodium_limit": case.get("sodium_limit"),

            # Existing classification field only.
            # Not used as a diabetes pass/fail rule.
            "sugar_limit": 10
        })

output = ROOT / "recipes_for_validation.json"

output.write_text(
    json.dumps(
        export,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print(
    f"Exported {len(export)} recipes "
    f"to {output.name}"
)
