import json
import time
from pathlib import Path
from google.genai import errors
from compare import generate_one
from config import CARB_LIMIT_G, SODIUM_LIMIT_MG

ROOT = Path(__file__).resolve().parent
TEST_PATH = ROOT / "test_cases.json"
RESULTS_PATH = ROOT / "all_results.json"
METHODS = ("prompt_only", "rag_assisted")

def save_atomic(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def validate_case(case):
    case = dict(case)
    case["carb_limit"] = CARB_LIMIT_G if case.get("diabetes") else None
    case["sodium_limit"] = SODIUM_LIMIT_MG if case.get("hypertension") else None
    return case

def main():
    cases = [validate_case(c) for c in load_json(TEST_PATH, [])]
    if len(cases) != 20 or len({c["id"] for c in cases}) != 20:
        raise ValueError("Expected exactly 20 unique test cases")
    existing = load_json(RESULTS_PATH, [])
    by_id = {r["test_case"]["id"]: r for r in existing}
    # Important: do not mix older runs with different limits/cases.
    for case in cases:
        old = by_id.get(case["id"])
        if old and old["test_case"] != case:
            raise ValueError(f"Case {case['id']} changed. Back up/delete all_results.json before restarting")
        by_id.setdefault(case["id"], {"test_case": case})
    for case in cases:
        result = by_id[case["id"]]
        for method in METHODS:
            if method in result:
                print(f"Skipping {case['id']} {method}: already saved")
                continue
            for attempt in range(1, 4):
                try:
                    print(f"Generating {case['id']} {method} (attempt {attempt})")
                    result[method] = generate_one(case, method)
                    save_atomic(RESULTS_PATH, [by_id[c["id"]] for c in cases])
                    break
                except (errors.ServerError, errors.ClientError) as exc:
                    status = getattr(exc, "code", None)
                    if status not in (429, 500, 502, 503, 504) or attempt == 3:
                        print(f"Stopped on {case['id']} {method}: {exc}")
                        return
                    time.sleep(10 * attempt)
                except Exception as exc:
                    print(f"Stopped on {case['id']} {method}: {exc}")
                    return
    print("Done: 20 cases / 40 generated recipes saved in all_results.json")

if __name__ == "__main__":
    main()
