import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "eco_summary_exists": False,
        "valid_json": False,
        "correct_total_organic_seeds": False,
        "correct_watering_order": False,
        "used_botanical_skill": False
    }

    summary_path = "deliverables/eco_summary.json"
    
    # Check if folder exists
    if os.path.exists("deliverables") and os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True

    # Check the summary file
    if os.path.exists(summary_path):
        state["eco_summary_exists"] = True
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["valid_json"] = True
                
                # LOGIC:
                # Organic Seeds:
                # - PDF: Tomato(120), Carrot(85), Cucumber(40) = 245
                # - TXT: Pumpkin(35), Tomato(12) = 47
                # Total = 292
                
                # Watering Days:
                # - Cucumber: 1 (from PDF)
                # - Tomato: 2 (from PDF)
                # - Pumpkin: 3 (Must be retrieved from botanical_watering_algorithm_skill)
                # - Carrot: 4 (from PDF)
                # Expected order: Cucumber, Tomato, Pumpkin, Carrot
                
                found_total = False
                found_list = False
                
                for v in data.values():
                    if isinstance(v, (int, float)) and v == 292:
                        found_total = True
                    if isinstance(v, list) and len(v) == 4:
                        lower_list = [str(x).lower() for x in v]
                        if lower_list == ["cucumber", "tomato", "pumpkin", "carrot"]:
                            found_list = True
                
                state["correct_total_organic_seeds"] = found_total
                state["correct_watering_order"] = found_list
        except:
            pass

    # Check skill usage via trace would be in verify_prompt, 
    # but we can look for evidence of the tool's output being handled.
    # For now, verify_rules handles objective file state.
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
