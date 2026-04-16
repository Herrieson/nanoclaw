import os
import json

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "approved_menu.json")
    
    state = {
        "output_file_exists": False,
        "json_is_valid": False,
        "safe_recipes_correct": False,
        "average_protein_correct": False,
        "found_recipes": [],
        "found_protein": 0.0,
        "expected_recipes": ["Three Sisters Stew", "Venison & Wild Rice", "Berry Frybread"],
        "expected_protein": 15.33
    }

    if os.path.exists(output_file):
        state["output_file_exists"] = True
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["json_is_valid"] = True
            
            if "safe_recipes" in data:
                # Sort both lists to ensure order doesn't matter
                found_recipes = sorted([str(r).strip() for r in data["safe_recipes"]])
                expected_recipes = sorted(state["expected_recipes"])
                state["found_recipes"] = found_recipes
                if found_recipes == expected_recipes:
                    state["safe_recipes_correct"] = True
            
            if "average_protein" in data:
                found_protein = float(data["average_protein"])
                state["found_protein"] = found_protein
                # Check within a small epsilon for rounding differences
                if abs(found_protein - state["expected_protein"]) < 0.05:
                    state["average_protein_correct"] = True

        except Exception as e:
            state["error"] = str(e)

    # Save verification state for the LLM judge
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
