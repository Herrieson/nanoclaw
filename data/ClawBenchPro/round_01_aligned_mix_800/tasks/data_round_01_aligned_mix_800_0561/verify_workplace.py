import os
import sys
import json
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "deliverables/summary.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    details = []
    total_score = 0

    # 1. Check file existence (10 points)
    if not os.path.exists(output_path):
        details.append({"item": "Check deliverables/summary.json existence", "score": 0, "max_score": 10, "passed": False, "reason": "Output file not found."})
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    details.append({"item": "Check deliverables/summary.json existence", "score": 10, "max_score": 10, "passed": True, "reason": "Output file exists."})
    
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON parsing", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": 10, "details": details}, f)
        return

    # 2. Total Guests Validation (20 points)
    # Expected: 100 (Based on env_builder logic: 40 active users, pattern (i%4)+1 results in 100)
    expected_guests = 100
    actual_guests = data.get("total_guests")
    if actual_guests == expected_guests:
        details.append({"item": "Guest count accuracy", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly calculated 100 guests."})
        total_score += 20
    else:
        details.append({"item": "Guest count accuracy", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected 100, got {actual_guests}. Likely failed to handle cancellations or misinterpreted the chat pattern."})

    # 3. Restrictions Validation (20 points)
    # Expected: sorted(["vegan", "peanut-allergy", "dairy-free", "gluten-free"])
    expected_restrictions = sorted(["vegan", "peanut-allergy", "dairy-free", "gluten-free"])
    actual_restrictions = sorted(data.get("restrictions", []))
    if actual_restrictions == expected_restrictions:
        details.append({"item": "Restrictions master list", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly identified unique restrictions of active guests."})
        total_score += 20
    else:
        details.append({"item": "Restrictions master list", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_restrictions}, got {actual_restrictions}. Likely included restrictions from cancelled users."})

    # 4. Safe Recipes Validation (20 points)
    # Expected: sorted(["Avocado Cacao Mousse", "Golden Lentil Stew", "Stuffed Bell Peppers"])
    expected_recipes = sorted(["Avocado Cacao Mousse", "Golden Lentil Stew", "Stuffed Bell Peppers"])
    actual_recipes = sorted(data.get("safe_recipes", []))
    if actual_recipes == expected_recipes:
        details.append({"item": "Recipe selection (Verified & Safe)", "score": 20, "max_score": 20, "passed": True, "reason": "Selected correct golden recipes."})
        total_score += 20
    else:
        details.append({"item": "Recipe selection (Verified & Safe)", "score": 0, "max_score": 20, "passed": False, "reason": f"Recipe list mismatch. Expected {expected_recipes}, got {actual_recipes}."})

    # 5. Shopping List Calculations (30 points)
    # Calculations (Scale Factor for 100 guests):
    # Mousse (serves 20): Factor 5. Avocados: 4*5=20, Cacao: 10*5=50, Salt: 0.5*5=2.5
    # Stew (serves 10): Factor 10. Lentils: 4*10=40, Broth: 2*10=20, Salt: 2*10=20
    # Peppers (serves 5): Factor 20. Bell peppers: 5*20=100, Rice: 2*20=40, Salt: 1*20=20
    # Combined Totals:
    # avocados: 20, cacao powder (tbsp): 50, salt (tsp): 2.5 + 20 + 20 = 42.5, lentils (cups): 40, broth (liters): 20, bell peppers: 100, rice (cups): 40
    expected_shopping = {
        "avocados": 20,
        "cacao powder (tbsp)": 50,
        "salt (tsp)": 42.5,
        "lentils (cups)": 40,
        "broth (liters)": 20,
        "bell peppers": 100,
        "rice (cups)": 40
    }
    
    actual_shopping = data.get("shopping_list", {})
    correct_ingredients = 0
    total_ingredients = len(expected_shopping)
    
    for ing, val in expected_shopping.items():
        actual_val = actual_shopping.get(ing)
        if actual_val is not None and math.isclose(float(actual_val), float(val), rel_tol=1e-5):
            correct_ingredients += 1
            
    ing_score = int((correct_ingredients / total_ingredients) * 30)
    if correct_ingredients == total_ingredients:
        details.append({"item": "Shopping list calculations", "score": 30, "max_score": 30, "passed": True, "reason": "All ingredients correctly scaled and aggregated."})
    else:
        details.append({"item": "Shopping list calculations", "score": ing_score, "max_score": 30, "passed": False, "reason": f"Only {correct_ingredients}/{total_ingredients} ingredients calculated correctly."})
    
    total_score += (10 + ing_score) # 10 for JSON structure/existence already accounted at start

    final_result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    
    with open(score_file, "w") as f:
        json.dump(final_result, f, indent=2)

if __name__ == "__main__":
    verify()
