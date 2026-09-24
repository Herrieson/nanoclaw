import os
import json
import sys

def verify():
    state = {
        "grocery_dir_exists": False,
        "list_json_exists": False,
        "is_valid_json": False,
        "calculated_apples_correct": False,
        "calculated_flour_correct": False,
        "calculated_sugar_correct": False,
        "calculated_butter_correct": False,
        "calculated_vanilla_correct": False,
        "no_expensive_ingredients": True
    }

    grocery_path = "grocery"
    json_path = os.path.join(grocery_path, "list.json")

    if os.path.isdir(grocery_path):
        state["grocery_dir_exists"] = True
    
    if os.path.isfile(json_path):
        state["list_json_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            
            state["is_valid_json"] = True
            
            normalized_data = {k.lower(): v for k, v in data.items()}
            
            if float(normalized_data.get("apples", 0)) == 9.0:
                state["calculated_apples_correct"] = True
            if float(normalized_data.get("flour", 0)) == 9.0:
                state["calculated_flour_correct"] = True
            if float(normalized_data.get("sugar", 0)) == 4.5:
                state["calculated_sugar_correct"] = True
            if float(normalized_data.get("butter", 0)) == 6.0:
                state["calculated_butter_correct"] = True
            if float(normalized_data.get("vanilla", 0)) == 3.0:
                state["calculated_vanilla_correct"] = True
                
            forbidden = ["saffron", "truffle", "caviar", "chocolate", "cream", "eggs"]
            for item in forbidden:
                if item in normalized_data:
                    state["no_expensive_ingredients"] = False

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
