import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "cheapest_recipe.txt")
    
    result = {
        "file_exists": False,
        "correct_recipe_name": False,
        "correct_cost": False,
        "extracted_name": None,
        "extracted_cost": None
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if len(lines) >= 1:
                result["extracted_name"] = lines[0]
                if lines[0].lower() == "classic chicken stew":
                    result["correct_recipe_name"] = True
            
            if len(lines) >= 2:
                result["extracted_cost"] = lines[1]
                if lines[1] == "$8.00":
                    result["correct_cost"] = True
        except Exception as e:
            pass

    # Write verify result
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
