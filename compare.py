from prompt_only import generate_recipe
from rag import generate_rag_recipe

def generate_one(case, method):
    fn = {"prompt_only": generate_recipe, "rag_assisted": generate_rag_recipe}[method]
    return fn(
        ingredients=case["ingredients"], allergies=case.get("allergies", []),
        diabetes=case.get("diabetes", False),
        hypertension=case.get("hypertension", False),
        carb_limit=case.get("carb_limit"), sodium_limit=case.get("sodium_limit")
    )

def compare_methods(ingredients, allergies, diabetes=False, hypertension=False,
                    carb_limit=None, sodium_limit=None):
    case = dict(ingredients=ingredients, allergies=allergies, diabetes=diabetes,
                hypertension=hypertension, carb_limit=carb_limit, sodium_limit=sodium_limit)
    return {"test_case": case, "prompt_only": generate_one(case, "prompt_only"),
            "rag_assisted": generate_one(case, "rag_assisted")}
