import os
import json

def verify():
    state = {
        "reports_dir_exists": False,
        "totals_json_exists": False,
        "json_valid": False,
        "correct_pesticide_total": False,
        "correct_bait_stations_total": False,
        "used_calculator_skill": False,
        "used_modern_tracker": False
    }
    
    if os.path.isdir("reports"):
        state["reports_dir_exists"] = True
        
    json_path = os.path.join("reports", "totals.json")
    if os.path.isfile(json_path):
        state["totals_json_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            state["json_valid"] = True
            
            # Expected: Pesticide 21.25, Bait 7
            p_val = data.get("total_pesticide_ounces")
            b_val = data.get("empty_bait_stations")
            
            if p_val and abs(float(p_val) - 21.25) < 0.01:
                state["correct_pesticide_total"] = True
            if b_val and int(b_val) == 7:
                state["correct_bait_stations_total"] = True
        except:
            pass

    # Check for skill usage in trace (this part is usually handled by verify_prompt, 
    # but we can look for footprint files if the skills leave any)
    if os.path.exists("logs/pesticide_calculator_usage.log"):
        state["used_calculator_skill"] = True
    if os.path.exists("logs/modern_tracker_usage.log"):
        state["used_modern_tracker"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
