import os
import json

def verify():
    target_file = "potluck_prep.json"
    state = {
        "file_exists": False,
        "valid_json": False,
        "safe_recipes_correct": False,
        "shopping_list_correct": False,
        "errors": []
    }

    if not os.path.exists(target_file):
        state["errors"].append("potluck_prep.json does not exist.")
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        state["valid_json"] = True
    except Exception as e:
        state["errors"].append(f"Invalid JSON: {str(e)}")
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    expected_safe = {"Haupia", "Poi", "Sweet Potato (Uala)"}
    actual_safe = set(data.get("safe_recipes", []))
    
    if actual_safe == expected_safe:
        state["safe_recipes_correct"] = True
    else:
        state["errors"].append(f"Safe recipes incorrect. Expected {expected_safe}, got {actual_safe}")

    # Expected math:
    # Haupia (scale 25/8 = 3.125): coconut milk=12.5, sugar=1.5625, cornstarch=15.625, water=1.5625
    # Poi (scale 25/4 = 6.25): taro root=12.5, water=6.25
    # Sweet Potato (scale 25/5 = 5.0): purple sweet potatoes=15.0, coconut milk=5.0, salt=2.5
    # Combined:
    # coconut milk: 17.5
    # sugar: 1.56
    # cornstarch: 15.63 or 15.62
    # water: 7.81
    # taro root: 12.5
    # purple sweet potatoes: 15.0
    # salt: 2.5
    
    expected_list = {
        "coconut milk (cups)": 17.5,
        "sugar (cups)": 1.5625,
        "cornstarch (tbsp)": 15.625,
        "water (cups)": 7.8125,
        "taro root (lbs)": 12.5,
        "purple sweet potatoes (lbs)": 15.0,
        "salt (tsp)": 2.5
    }

    actual_list = data.get("shopping_list", {})
    list_correct = True
    
    for key, expected_val in expected_list.items():
        if key not in actual_list:
            state["errors"].append(f"Missing ingredient in shopping list: {key}")
            list_correct = False
            continue
        
        # Check within rounding tolerance (rounded to 2 decimal places expected)
        actual_val = float(actual_list[key])
        if abs(actual_val - expected_val) > 0.03:
            state["errors"].append(f"Incorrect amount for {key}. Expected ~{expected_val}, got {actual_val}")
            list_correct = False

    # Check for unwanted extra ingredients
    for key in actual_list.keys():
        if key not in expected_list:
            state["errors"].append(f"Unexpected extra ingredient in shopping list: {key}")
            list_correct = False

    state["shopping_list_correct"] = list_correct

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
