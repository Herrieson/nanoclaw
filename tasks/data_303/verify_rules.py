import os
import json
import math

def verify():
    result = {
        "success": False,
        "reason": "",
        "state": {}
    }
    
    target_file = "scaled_recipe.json"
    
    if not os.path.exists(target_file):
        result["reason"] = f"{target_file} not found in the workspace."
        return result
        
    try:
        with open(target_file, 'r') as f:
            data = json.load(f)
            
        result["state"]["submitted_json"] = data
        
        # Expected calculation: Original servings = 4, Target = 50. Multiplier = 12.5
        expected = {
            "flour": 50.0,
            "buttermilk": 18.75,
            "caraway_seeds": 12.5,
            "dried_currants": 6.25,
            "orange_zest": 25.0,
            "salt": 12.5,
            "baking_soda": 12.5
        }
        
        # Normalize keys to lower case for loose matching
        normalized_data = {k.lower(): float(v) for k, v in data.items()}
        
        # Check if all expected ingredients are present and values match
        missing = []
        wrong_values = []
        for key, exp_val in expected.items():
            if key not in normalized_data:
                # try finding substring just in case
                found = False
                for k in normalized_data.keys():
                    if key in k or k in key:
                        if math.isclose(normalized_data[k], exp_val, rel_tol=1e-3):
                            found = True
                            break
                if not found:
                    missing.append(key)
            else:
                if not math.isclose(normalized_data[key], exp_val, rel_tol=1e-3):
                    wrong_values.append(f"{key}: expected {exp_val}, got {normalized_data[key]}")
                    
        if missing:
            result["reason"] = f"Missing ingredients in output: {', '.join(missing)}"
        elif wrong_values:
            result["reason"] = f"Incorrect scaling values: {'; '.join(wrong_values)}"
        else:
            result["success"] = True
            result["reason"] = "JSON formatted perfectly with correct scaled values."
            
    except Exception as e:
        result["reason"] = f"Error reading or parsing {target_file}: {str(e)}"
        
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)
        
    print(json.dumps(result))

if __name__ == "__main__":
    verify()
