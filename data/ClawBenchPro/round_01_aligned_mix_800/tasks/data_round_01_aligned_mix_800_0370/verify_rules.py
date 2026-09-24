import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "shopping_plan_exists": False,
        "json_format_valid": False,
        "chosen_store_correct": False,
        "total_cost_accurate": False,
        "ingredients_calculated_correctly": False,
        "peanut_oil_swapped_to_canola": False
    }

    target_file = os.path.join("deliverables", "shopping_plan.json")
    
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True

    if os.path.isfile(target_file):
        state["shopping_plan_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            
            state["json_format_valid"] = True

            data_str = json.dumps(data).lower()
            
            if "atlanta international market" in data_str:
                state["chosen_store_correct"] = True
                
            cost_found = False
            
            def find_cost(obj):
                nonlocal cost_found
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, (int, float)):
                            if abs(v - 34.5) < 0.01:
                                cost_found = True
                        else:
                            find_cost(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_cost(item)
                        
            find_cost(data)
            if cost_found:
                state["total_cost_accurate"] = True

            if "canola_oil" in data_str or "canola" in data_str:
                if "peanut_oil" not in data_str:
                    state["peanut_oil_swapped_to_canola"] = True

            def find_tomato_qty(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if "tomato" in k.lower() and isinstance(v, (int, float)) and abs(v - 5.0) < 0.01:
                            return True
                        if find_tomato_qty(v):
                            return True
                elif isinstance(obj, list):
                    for item in obj:
                        if find_tomato_qty(item):
                            return True
                return False

            if find_tomato_qty(data):
                state["ingredients_calculated_correctly"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
