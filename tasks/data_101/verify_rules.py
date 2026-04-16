import os
import json

def verify():
    # Costs calculated manually:
    # Bratwurst Tacos: (2*1.5) + (3*0.2) + (1*0.5) = 3.0 + 0.6 + 0.5 = 4.1
    # Soul Food Ramen: (1*0.8) + (2*1.0) + (1*2.5) = 0.8 + 2.0 + 2.5 = 5.3
    # Spicy Schnitzel: (1*2.0) + (2*0.3) + (1*0.4) = 2.0 + 0.6 + 0.4 = 3.0
    
    expected_costs = {
        "Bratwurst Tacos": 4.1,
        "Soul Food Ramen": 5.3,
        "Spicy Schnitzel": 3.0
    }
    
    workspace_dir = "." # Target workspace
    target_file = os.path.join(workspace_dir, "menu_costs.json")
    
    result = {
        "menu_costs_exists": False,
        "correct_recipes_found": False,
        "no_distractors": False,
        "prices_accurate": False,
        "details": {}
    }

    if not os.path.exists(target_file):
        return result

    result["menu_costs_exists"] = True
    
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
            
        found_keys = set(data.keys())
        expected_keys = set(expected_costs.keys())
        
        if found_keys.issuperset(expected_keys):
            result["correct_recipes_found"] = True
            
        if "Classic Cheeseburger" not in found_keys:
            result["no_distractors"] = True
            
        prices_correct = True
        for k, v in expected_costs.items():
            if k in data and abs(float(data[k]) - v) < 0.01:
                result["details"][k] = "Correct"
            else:
                prices_correct = False
                result["details"][k] = f"Expected {v}, Got {data.get(k, 'Missing')}"
                
        result["prices_accurate"] = prices_correct
        
    except Exception as e:
        result["details"]["error"] = str(e)
        
    # Write structural verification state
    with open(os.path.join(workspace_dir, "state.json"), "w") as f:
        json.dump(result, f, indent=2)

    return result

if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
