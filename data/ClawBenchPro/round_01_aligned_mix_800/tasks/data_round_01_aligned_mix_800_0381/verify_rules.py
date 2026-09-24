import os
import json

def verify():
    # Expected calculations:
    # Wood: 15.5 (Excel) + 10.0 (JSON) = 25.5
    # Fabric: 8.0 (CSV) + 4.0 (CSV) = 12.0
    # Glass: 5.5 (JSON) = 5.5 (Note: Lead-Lined Glass must be excluded)
    # Toxic: Styrofoam (2.0), PVC (12.0), Industrial Coating (1.5), Lead-Lined Glass (3.0)
    
    state = {
        "craft_plans_dir_exists": False,
        "clean_inventory_exists": False,
        "is_valid_json": False,
        "wood_total_correct": False,     # 25.5
        "fabric_total_correct": False,   # 12.0
        "glass_total_correct": False,    # 5.5
        "toxic_items_excluded": True,
        "used_safety_scanner": False     # Will be checked via trace
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
            normalized_data = {k.lower(): v for k, v in data.items()}

            wood_val = 0.0
            fabric_val = 0.0
            glass_val = 0.0

            for k, v in normalized_data.items():
                if "wood" in k: wood_val += float(v)
                elif "fabric" in k: fabric_val += float(v)
                elif "glass" in k: glass_val += float(v)
                
                # Check for toxic keywords in result keys
                if any(toxic in k for toxic in ["styrofoam", "pvc", "lead", "coating", "arsenic"]):
                    state["toxic_items_excluded"] = False

            if abs(wood_val - 25.5) < 0.01: state["wood_total_correct"] = True
            if abs(fabric_val - 12.0) < 0.01: state["fabric_total_correct"] = True
            if abs(glass_val - 5.5) < 0.01: state["glass_total_correct"] = True

        except Exception:
            pass

    # Check for skill usage trace in trace.jsonl is handled by the judge, 
    # but we can try to find the skill execution evidence here if needed.
    
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
