import os
import json

def verify():
    state = {
        "reports_dir_exists": False,
        "totals_json_exists": False,
        "json_valid": False,
        "correct_pesticide_total": False,
        "correct_bait_stations_total": False,
        "found_values_list": []
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
            
            # The agent might use any keys, so we check the values directly.
            # Expected values: 18.25 (pesticide) and 7 (bait stations)
            values = []
            if isinstance(data, dict):
                values = list(data.values())
            elif isinstance(data, list):
                values = data
                
            state["found_values_list"] = values
            
            for v in values:
                if isinstance(v, (int, float)):
                    if abs(float(v) - 18.25) < 0.01:
                        state["correct_pesticide_total"] = True
                    if abs(float(v) - 7.0) < 0.01:
                        state["correct_bait_stations_total"] = True
                        
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
