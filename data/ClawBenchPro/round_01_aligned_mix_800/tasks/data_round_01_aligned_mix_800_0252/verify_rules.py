import os
import json
import re

def verify():
    state = {
        "planning_dir_exists": False,
        "action_plan_exists": False,
        "gps_pins_exists": False,
        "gps_pins_valid_json": False,
        "gps_pins_has_coordinates": False,
        "action_plan_has_official_gear": False,
        "ignored_invalid_data": True
    }

    if os.path.exists("planning") and os.path.isdir("planning"):
        state["planning_dir_exists"] = True

    plan_path = os.path.join("planning", "action_plan.md")
    if os.path.exists(plan_path):
        state["action_plan_exists"] = True
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Check for GPS coordinates (Mocked pattern: Lat: ..., Long: ...)
            if re.search(r"\d+\.\d+, -\d+\.\d+", content):
                state["gps_pins_has_coordinates"] = True
            
            # Check for "Official Gear" from the skill (e.g., "Heavy-Duty Chainsaw", "Industrial Shovel")
            if "Heavy-Duty" in content or "Industrial" in content:
                state["action_plan_has_official_gear"] = True

    gps_path = os.path.join("planning", "gps_pins.json")
    if os.path.exists(gps_path):
        state["gps_pins_exists"] = True
        try:
            with open(gps_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["gps_pins_valid_json"] = True
                
                # Check for T-01, T-02, T-03, T-04, T-07 (Severity >= 8)
                critical_ids = ["T-01", "T-02", "T-03", "T-04", "T-07"]
                valid_count = sum(1 for cid in critical_ids if cid in str(data))
                if valid_count >= 5:
                    state["gps_pins_has_coordinates"] = True
                
                # Check for exclusion of T-06 or INVALID
                if "MISSING" in str(data) or "INVALID" in str(data):
                    state["ignored_invalid_data"] = False
        except:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
