import os
import json

def verify():
    results = {
        "summary_exists": False,
        "correct_categories_total": False,
        "missing_ingredients_accurate": False,
        "deduplication_performed": False
    }

    file_path = "pantry_audit/summary.json"
    if os.path.exists(file_path):
        results["summary_exists"] = True
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
                # Check Category Totals (Logic check)
                # Categories determined via tools now.
                # Protein: Chicken Breast (12.5*3) + Beef Roast (22) = 59.5
                # Produce: Apples (5*3) + Potatoes (6) + Carrots (2*2) = 25.0
                # Grains: Flour (4) + Sugar (2.5*2) + Yeast (1.5*5) = 16.5
                totals = data.get("category_spending", {})
                if (float(totals.get("Protein", 0)) == 59.5 and 
                    float(totals.get("Produce", 0)) == 25.0):
                    results["correct_categories_total"] = True
                
                # Check Missing Ingredients
                # Bought: Chicken, Flour, Apples, Sugar, Buttermilk, Potatoes, Beef Roast, Carrots, Yeast
                # Stew needs: Onions, Beef Stock (Missing)
                # Bread needs: Baking Soda, Salt (Missing)
                missing = data.get("missing_ingredients", [])
                expected_missing = {"Onions", "Beef Stock", "Baking Soda", "Salt"}
                if set(missing) == expected_missing:
                    results["missing_ingredients_accurate"] = True
                
                # Check Deduplication (Chicken Breast was in 2 rows, quantity should be 3 total)
                inventory = data.get("inventory", [])
                chicken_entries = [i for i in inventory if "Chicken" in str(i) or "Chicken Breast" in str(i)]
                # Deduplication means merging it into one entry, or correctly aggregating quantity.
                # If they just appended both without summing, that's poor deduplication.
                if len(inventory) > 0 and len(chicken_entries) == 1:
                     results["deduplication_performed"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
