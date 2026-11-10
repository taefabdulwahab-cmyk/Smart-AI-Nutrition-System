"""Merge independently computed Jumana validation records. Never invent results."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
recipes = json.loads((ROOT / "all_results.json").read_text(encoding="utf-8"))
checks = json.loads((ROOT / "validation_results.json").read_text(encoding="utf-8"))
by_key = {}
for v in checks:
    key = (v["test_case_id"], v["method"])
    if key in by_key:
        raise ValueError(f"Duplicate validation record: {key}")
    if v.get("status") not in ("PASS", "FAIL", "UNVERIFIABLE"):
        raise ValueError(f"Missing or invalid status: {key}")
    for field in ("carbs_g", "sodium_mg", "sugar_g", "violations"):
        if field not in v:
            raise ValueError(f"Missing {field} for {key}")
    if not isinstance(v["violations"], list):
        raise ValueError(f"violations must be a list: {key}")
    by_key[key] = v
expected = {(r["test_case"]["id"], m) for r in recipes for m in ("prompt_only", "rag_assisted") if m in r}
missing = expected - by_key.keys()
extra = by_key.keys() - expected
if missing or extra:
    raise ValueError(f"Validation mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
for row in recipes:
    row["validation"] = {m: by_key[(row["test_case"]["id"], m)] for m in ("prompt_only", "rag_assisted") if m in row}
(ROOT / "final_results.json").write_text(json.dumps(recipes, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Created final_results.json with {len(by_key)} validated recipes")
