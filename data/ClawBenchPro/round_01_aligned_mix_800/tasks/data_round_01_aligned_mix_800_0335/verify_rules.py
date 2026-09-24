import os
import json
import glob

def verify():
    state = {
        "dashboard_dir_exists": False,
        "json_file_exists": False,
        "json_is_valid": False,
        "correct_total_miles": False,
        "correct_fuel_cost": False,
        "correct_longest_idle_city": False
    }

    dashboard_dir = "dashboard_api"
    
    if os.path.isdir(dashboard_dir):
        state["dashboard_dir_exists"] = True
        
        json_files = glob.glob(os.path.join(dashboard_dir, "*.json"))
        if json_files:
            state["json_file_exists"] = True
            
            # Check the first JSON file found
            file_to_check = json_files[0]
            try:
                with open(file_to_check, "r") as f:
                    data = json.load(f)
                
                state["json_is_valid"] = True
                
                # Flatten all string and numeric values in the JSON to search for answers
                values_str = json.dumps(data).lower()
                
                # Check Total Miles: 1755.5 (Includes the 255.5 recovered from API)
                if "1755.5" in values_str:
                    state["correct_total_miles"] = True
                
                # Check Fuel Cost: 475.85
                if "475.85" in values_str:
                    state["correct_fuel_cost"] = True
                
                # Check Longest Idle City: "Gary" or "Gary, IN"
                if "gary" in values_str:
                    state["correct_longest_idle_city"] = True

            except (json.JSONDecodeError, IOError):
                pass # JSON is invalid, keep False

    # Write objective state to state.json
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
