import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "kitchen_prep", "winning_recipe_order.json")
    
    state = {
        "file_created": False,
        "is_valid_json": False,
        "correct_recipe_name": False,
        "correct_cost": False,
        "correct_carbon": False,
        "has_ingredients_list": False
    }

    if os.path.exists(target_file):
        state["file_created"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            data_str = json.dumps(data).lower()
            
            if "eco_plantain_bowl" in data_str:
                state["correct_recipe_name"] = True
                
            # Expected Cost: 5.7, Expected Carbon: 9.9
            if "5.7" in data_str:
                state["correct_cost"] = True
            
            if "9.9" in data_str:
                state["correct_carbon"] = True
                
            if "plantain" in data_str and "blackbeans" in data_str and "rice" in data_str and "organicavocado" in data_str:
                state["has_ingredients_list"] = True

        except Exception:
            pass

    state_file = os.path.join(workspace, "state.json")
    with open(state_file, "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
