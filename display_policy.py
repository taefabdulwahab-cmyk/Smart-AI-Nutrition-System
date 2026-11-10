"""Use only for the user-facing UI; do not filter research experiment results."""
def visible_rag_recipe(result_row):
    validation = result_row.get("validation", {}).get("rag_assisted", {})
    if validation.get("status") == "PASS":
        return result_row.get("rag_assisted")
    return None  # FAIL/UNVERIFIABLE/NOT_EVALUATED: do not show recipe
