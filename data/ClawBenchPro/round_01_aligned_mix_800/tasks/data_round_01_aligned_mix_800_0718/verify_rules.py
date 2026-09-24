import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    best_recipe_path = os.path.join(deliverables_dir, "best_recipe.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_recipe_name": False,
        "correct_score": False,
        "correct_ingredients": False
    }

    if os.path.exists(best_recipe_path):
        state["file_exists"] = True
        try:
            with open(best_recipe_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # The correct answer is Aloe Soothe
            # Recipe A is natural, pH 5.4, score 9.2
            # Recipe B has pH 6.8 (invalid)
            # Recipe C has Dimethicone (synthetic) (invalid)
            # Recipe D is natural, pH 5.2, score 9.4. Highest valid score!
            
            data_str = json.dumps(data).lower()
            
            if "aloe soothe" in data_str:
                state["correct_recipe_name"] = True
            
            if "9.4" in data_str:
                state["correct_score"] = True
                
            if "aloe vera" in data_str and "shea butter" in data_str and "beeswax" in data_str:
                state["correct_ingredients"] = True

        except Exception:
            pass

    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
