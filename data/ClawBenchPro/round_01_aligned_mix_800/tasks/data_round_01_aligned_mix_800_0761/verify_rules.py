import os
import json

def verify():
    state = {
        "deliverables_dir_exists": False,
        "summary_json_exists": False,
        "summary_json_valid": False,
        "total_guests_correct": False,
        "restrictions_correct": False,
        "safe_recipes_correct": False,
        "shopping_list_correct": False
    }
    
    if os.path.isdir("deliverables"):
        state["deliverables_dir_exists"] = True
        if os.path.isfile("deliverables/summary.json"):
            state["summary_json_exists"] = True
            try:
                with open("deliverables/summary.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                state["summary_json_valid"] = True
                
                if data.get("total_guests") == 8:
                    state["total_guests_correct"] = True
                
                raw_restrictions = data.get("restrictions", [])
                if isinstance(raw_restrictions, list):
                    restrictions = [str(r).lower() for r in raw_restrictions]
                    if set(restrictions) == {"vegan", "peanut-allergy", "dairy-free"}:
                        state["restrictions_correct"] = True
                    
                raw_recipes = data.get("safe_recipes", [])
                if isinstance(raw_recipes, list):
                    if set(raw_recipes) == {"Jackfruit Carnitas Tacos", "Mango Avocado Salad"}:
                        state["safe_recipes_correct"] = True
                    
                shopping = data.get("shopping_list", {})
                expected_shopping = {
                    "jackfruit (cans)": 4,
                    "tortillas": 16,
                    "onion": 2,
                    "cilantro (bunch)": 1,
                    "mango": 4,
                    "avocado": 4,
                    "lime": 4
                }
                
                if isinstance(shopping, dict) and len(shopping) == len(expected_shopping):
                    shopping_match = True
                    for k, v in expected_shopping.items():
                        if k not in shopping:
                            shopping_match = False
                            break
                        try:
                            if float(shopping[k]) != float(v):
                                shopping_match = False
                                break
                        except (ValueError, TypeError):
                            shopping_match = False
                            break
                    if shopping_match:
                        state["shopping_list_correct"] = True
                    
            except Exception:
                pass
                
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
