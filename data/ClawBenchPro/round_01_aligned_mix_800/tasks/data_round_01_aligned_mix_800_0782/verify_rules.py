import os
import json

def evaluate_state():
    state = {
        "manager_report_exists": False,
        "found_total_donations": False,
        "found_dave_miller": False,
        "found_frank_wolf": False,
        "no_eve_adams_false_positive": True
    }

    report_dir = "manager_report"
    
    if os.path.isdir(report_dir):
        state["manager_report_exists"] = True
        
        combined_text = ""
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        combined_text += f.read().lower() + " "
                except Exception:
                    pass
        
        if "175" in combined_text:
            state["found_total_donations"] = True
            
        if "dave miller" in combined_text or "dave" in combined_text:
            state["found_dave_miller"] = True
            
        if "frank wolf" in combined_text or "frank" in combined_text:
            state["found_frank_wolf"] = True
            
        if "eve adams" in combined_text or "eve" in combined_text:
            state["no_eve_adams_false_positive"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    evaluate_state()
