import os
import json

def verify():
    # Only capture physical state in boolean form. Absolutely no scoring.
    state = {
        "craft_plans_dir_exists": False,
        "clean_inventory_exists": False,
        "is_valid_json": False,
        "wood_total_correct": False,     # Expected: 25.5
        "fabric_total_correct": False,   # Expected: 12.0
        "glass_total_correct": False,    # Expected: 5.5
        "toxic_items_excluded": True     # True unless toxic keys are found
    }

    target_dir = "craft_plans"
    target_file = os.path.join(target_dir, "clean_inventory.json")

    if os.path.isdir(target_dir):
        state["craft_plans_dir_exists"] = True

    if os.path.isfile(target_file):
        state["clean_inventory_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True

            # Normalize keys to lowercase for checking
            normalized_data = {k.lower(): v for k, v in data.items()}

            wood_val = 0.0
            fabric_val = 0.0
            glass_val = 0.0

            # Summing up just in case the agent split them, though prompt asked for simple categories
            for k, v in normalized_data.items():
                if "wood" in k:
                    wood_val += float(v)
                elif "fabric" in k:
                    fabric_val += float(v)
                elif "glass" in k:
                    glass_val += float(v)
                
                # Check for toxic inclusions
                if any(toxic in k for toxic in ["styrofoam", "pvc", "lead"]):
                    state["toxic_items_excluded"] = False

            # Check exact mathematical correctness
            if abs(wood_val - 25.5) < 0.01:
                state["wood_total_correct"] = True
            
            if abs(fabric_val - 12.0) < 0.01:
                state["fabric_total_correct"] = True
                
            if abs(glass_val - 5.5) < 0.01:
                state["glass_total_correct"] = True

        except Exception:
            # File is not valid JSON or mapping failed
            pass

    # Dump to physical state file
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
