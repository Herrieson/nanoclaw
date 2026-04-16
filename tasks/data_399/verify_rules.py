import os
import json
import sqlite3

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "report.json")
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "found_S005": False,
        "found_S008": False,
        "no_extra_sensors": False,
        "correct_values": False,
        "score": 0,
        "message": ""
    }
    
    if not os.path.exists(report_path):
        state["message"] = "report.json not found."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["report_exists"] = True
    
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except json.JSONDecodeError:
        state["message"] = "report.json is not valid JSON."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    expected_sensors = {"S-005", "S-008"}
    found_sensors = set(data.keys())
    
    if "S-005" in found_sensors: state["found_S005"] = True
    if "S-008" in found_sensors: state["found_S008"] = True
    
    if found_sensors == expected_sensors:
        state["no_extra_sensors"] = True
    
    # Check values
    try:
        val_005 = float(data.get("S-005", 999))
        val_008 = float(data.get("S-008", 999))
        
        # We know from the builder that absolute mins are 5.45 and 5.72
        if abs(val_005 - 5.45) < 0.01 and abs(val_008 - 5.72) < 0.01:
            state["correct_values"] = True
    except:
        pass

    score = 0
    if state["is_valid_json"]: score += 10
    if state["found_S005"] and state["found_S008"]: score += 40
    if state["no_extra_sensors"]: score += 20
    if state["correct_values"]: score += 30
    
    state["score"] = score
    state["message"] = "Verification completed."
    
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
