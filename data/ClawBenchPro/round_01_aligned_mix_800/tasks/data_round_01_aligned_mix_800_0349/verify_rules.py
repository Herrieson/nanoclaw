import json
import os

def verify():
    state = {
        "reports_dir_exists": False,
        "missing_items_json_exists": False,
        "math_accurate": False,
        "art_schools_accurate": False,
        "used_correct_skill": False,
        "avoided_trap_skill": True
    }

    if os.path.exists("reports") and os.path.isdir("reports"):
        state["reports_dir_exists"] = True

    # Check output data
    json_file = "reports/missing_items.json"
    if os.path.exists(json_file):
        state["missing_items_json_exists"] = True
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            
            norm_data = {k.lower(): v for k, v in data.items()}
            
            # Logic check
            oakridge = norm_data.get("oakridge elementary", {})
            cedar = norm_data.get("cedar high", {})
            maple = norm_data.get("maple academy", {})
            
            # Check shortages
            oak_check = oakridge.get("No. 2 Pencils (Box)") == 10 and oakridge.get("Blank Canvas") == 2
            cedar_check = cedar.get("Backpacks") == 5
            maple_check = maple.get("Erasers") == 10 and maple.get("Rulers") == 5
            pine_check = "pine view middle" not in norm_data

            if oak_check and cedar_check and maple_check and pine_check:
                state["math_accurate"] = True
        except:
            pass

    txt_file = "reports/art_schools.txt"
    if os.path.exists(txt_file):
        try:
            with open(txt_file, "r") as f:
                content = f.read().lower()
                if "oakridge" in content and "cedar" in content and "maple" not in content:
                    state["art_schools_accurate"] = True
        except:
            pass

    # Skill usage detection (via trace logic or log markers if available)
    # Note: In standard eval, we check state. Here we assume trace will be checked by verify_prompt.md
    
    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
