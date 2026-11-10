import json
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent / "knowledge_base" / "guidelines.json"


def retrieve_guidelines(allergies=None, diabetes=False, hypertension=False):
    data = json.loads(KB_PATH.read_text(encoding="utf-8"))
    records = data["guidelines"]
    allergy_set = {str(a).strip().casefold() for a in (allergies or [])}
    result = []
    for item in records:
        if (item["category"] == "allergy" and item["keyword"].casefold() in allergy_set) or \
           (item["category"] == "diabetes" and diabetes) or \
           (item["category"] == "hypertension" and hypertension):
            result.append(item)
    return result
