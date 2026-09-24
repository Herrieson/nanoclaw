import os
import json
import glob

def verify():
    state = {
        "output_folder_exists": False,
        "has_multiple_files": False,
        "found_scaffolding_hazard": False,
        "found_wire_hazard": False,
        "found_construction_total": False,
        "found_art_total": False,
        "no_minor_hazards_included": True
    }

    output_dir = "ready_for_monday"
    
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        state["output_folder_exists"] = True
        
        files = glob.glob(os.path.join(output_dir, "*"))
        files = [f for f in files if os.path.isfile(f)]
        
        if len(files) >= 2:
            state["has_multiple_files"] = True
            
        all_text = ""
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    all_text += f.read().lower() + "\n"
            except:
                pass

        # Check for explicit hazard reporting
        if "scaffolding" in all_text and "guardrail" in all_text:
            state["found_scaffolding_hazard"] = True
            
        if "live wire" in all_text and "sector 4" in all_text:
            state["found_wire_hazard"] = True

        # Ensure minor stuff wasn't included (following Marcus' strict instructions)
        if "dust mask" in all_text or "hard hat" in all_text:
            state["no_minor_hazards_included"] = False

        # Math verification
        # Construction total = 450 + 120 + 15 + 300 = 885
        if "885" in all_text:
            state["found_construction_total"] = True
            
        # Art total = 35.50 + 85 + 150 = 270.50
        if "270.5" in all_text:
            state["found_art_total"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
