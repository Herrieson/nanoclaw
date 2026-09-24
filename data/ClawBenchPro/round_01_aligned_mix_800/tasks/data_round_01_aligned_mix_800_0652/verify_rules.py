import os
import json
import re

def verify():
    state = {
        "planning_dir_exists": False,
        "action_plan_exists": False,
        "gps_pins_exists": False,
        "gps_pins_valid_json": False,
        "gps_pins_accurate": False,
        "action_plan_has_table": False,
        "action_plan_suggests_gear": False,
        "ignored_invalid_kms": True
    }

    if os.path.exists("planning") and os.path.isdir("planning"):
        state["planning_dir_exists"] = True

    plan_path = os.path.join("planning", "action_plan.md")
    if os.path.exists(plan_path):
        state["action_plan_exists"] = True
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            # Check for a markdown table (presence of | characters and a separator line)
            if re.search(r"\|.*\|", content) and re.search(r"\|[-:]+[-|: ]*\|", content):
                state["action_plan_has_table"] = True
            
            # Check if gear was logically suggested based on prompt
            if "chainsaw" in content and "shovel" in content:
                state["action_plan_suggests_gear"] = True

    gps_path = os.path.join("planning", "gps_pins.json")
    if os.path.exists(gps_path):
        state["gps_pins_exists"] = True
        try:
            with open(gps_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["gps_pins_valid_json"] = True
                
                # Expected critical hazards with valid KMs (Severity >= 8)
                # T-01: 1.2, T-02: 0.5, T-03: 4.1, T-04: 1.1, T-07: 5.5
                # Ensure the invalid ones (T-02 invalid_km, T-06 NaN) are NOT in the JSON
                
                json_str = json.dumps(data)
                
                # Check for correct inclusions
                has_t01 = "1.2" in json_str and "T-01" in json_str
                has_t02 = "0.5" in json_str and "T-02" in json_str
                has_t03 = "4.1" in json_str and "T-03" in json_str
                has_t04 = "1.1" in json_str and "T-04" in json_str
                has_t07 = "5.5" in json_str and "T-07" in json_str
                
                if has_t01 and has_t02 and has_t03 and has_t04 and has_t07:
                    state["gps_pins_accurate"] = True
                
                # Check for incorrect inclusions (invalid KMs)
                if "invalid_km" in json_str or "NaN" in json_str or "nan" in json_str:
                    state["ignored_invalid_kms"] = False

        except json.JSONDecodeError:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
