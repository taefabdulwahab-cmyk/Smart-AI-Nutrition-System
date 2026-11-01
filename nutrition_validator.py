
import csv
import re
from dataclasses import dataclass
from pathlib import Path


# ==========================================
# Ingredient Amount
# ==========================================

@dataclass
class IngredientAmount:
    name: str
    grams: float


# ==========================================
# Helpers
# ==========================================

def normalize_name(name):
    """Normalize ingredient names for matching."""
    name = str(name).strip().lower()
    name = re.sub(r"\s+", " ", name)
    return name


def normalize_column(name):
    """Normalize CSV column names."""
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        str(name).strip().lower()
    ).strip("_")


def number_from_cell(value):
    """Convert a CSV cell into a number."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if not value or value.lower() in {
        "na", "n/a", "none", "null", "nan", "-"
    }:
        return None

    # Handle numeric values stored as text
    try:
        result = float(value.replace(",", ""))

        if result < 0:
            return None

        return result

    except (ValueError, TypeError):
        return None


# ==========================================
# Nutrition Validator
# ==========================================

class NutritionValidator:

    def __init__(self, csv_file=None):

        if csv_file is None:
            csv_file = Path(__file__).parent / "data" / "ingredients_nutrition_allergen_review.csv"

        self.csv_file = Path(csv_file)
        self.items = {}

        self.load_data()

    # --------------------------------------
    # Load CSV
    # --------------------------------------

    def load_data(self):

        if not self.csv_file.exists():
            raise FileNotFoundError(
                f"Nutrition CSV not found: {self.csv_file}"
            )

        with open(
            self.csv_file,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "The CSV file has no column headers."
                )

            for original_row in reader:

                # Normalize column names
                row = {
                    normalize_column(key): value
                    for key, value in original_row.items()
                    if key is not None
                }

                # Find ingredient name column
                name_keys = [
                    "name",
                    "ingredient",
                    "ingredient_name",
                    "food",
                    "food_name",
                    "class",
                    "class_name"
                ]

                ingredient_name = None

                for key in name_keys:
                    value = row.get(key)

                    if value and str(value).strip():
                        ingredient_name = str(value).strip()
                        break

                if not ingredient_name:
                    continue

                key = normalize_name(ingredient_name)

                # Store ingredient record
                self.items[key] = row

        if not self.items:
            raise ValueError(
                "No ingredients were loaded from the CSV. "
                "Check the ingredient name column."
            )

        print(
            f"Loaded {len(self.items)} ingredients "
            f"from nutrition CSV."
        )
