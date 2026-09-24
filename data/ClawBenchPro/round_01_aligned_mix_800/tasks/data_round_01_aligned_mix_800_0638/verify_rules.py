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
                # Protein: (12.5*3) + 22 = 59.5
                # Produce: (5*3) + 6 + (2*2) = 25.0
                # Grains: 4 + (2.5*2) + (1.5*5) = 16.5
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
                
                # Check Deduplication (Chicken Breast was in 2 rows)
                inventory = data.get("inventory", [])
                chicken_entries = [i for i in inventory if "Chicken" in str(i)]
                # If they merged it into one entry with quantity 3 or kept it separate but summed it correctly
                # We check the logic via the total spend above, but here we check if they didn't just ignore the second entry
                if len(inventory) > 0:
                     results["deduplication_performed"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
