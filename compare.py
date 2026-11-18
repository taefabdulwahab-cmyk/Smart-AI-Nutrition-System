
from prompt_only import generate_recipe
from rag import generate_rag_recipe


def generate_one(case, method):
    """
    Generate a recipe using the selected method.
    Both methods return the same recipe JSON structure.
    """

    methods = {
        "prompt_only": generate_recipe,
        "rag_assisted": generate_rag_recipe
    }

    if method not in methods:
        raise ValueError(
            f"Unknown generation method: {method}"
        )

    return methods[method](
        ingredients=case["ingredients"],
        allergies=case.get("allergies", []),
        diabetes=case.get("diabetes", False),
        hypertension=case.get("hypertension", False),
        carb_limit=case.get("carb_limit"),
        sodium_limit=case.get("sodium_limit")
    )


def compare_methods(
    ingredients,
    allergies,
    diabetes=False,
    hypertension=False,
    carb_limit=None,
    sodium_limit=None
):
    """
    Generate recipes using Prompt-only and RAG-assisted
    with identical ingredients and dietary restrictions.
    """

    case = {
        "ingredients": ingredients,
        "allergies": allergies,
        "diabetes": diabetes,
        "hypertension": hypertension,
        "carb_limit": carb_limit,
        "sodium_limit": sodium_limit
    }

    return {
        "test_case": case,
        "prompt_only": generate_one(
            case, "prompt_only"
        ),
        "rag_assisted": generate_one(
            case, "rag_assisted"
        )
    }
