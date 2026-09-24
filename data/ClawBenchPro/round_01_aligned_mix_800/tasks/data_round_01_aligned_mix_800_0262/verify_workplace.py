import os
import json

def verify():
    state = {
        "report_exists": False,
        "valid_json": False,
        "has_correct_keys": False,
        "correct_stolen_plates": False,
        "correct_worst_hotspot": False
    }

    report_path = "reports/daily_briefing.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            state["valid_json"] = True
            
            if isinstance(data, dict) and "stolen_spotted" in data and "worst_hotspot" in data:
                state["has_correct_keys"] = True
                
                # Check stolen spotted (should be exactly XYZ-9999 and ABC-1234)
                spotted = data.get("stolen_spotted", [])
                if isinstance(spotted, list):
                    expected_stolen = {"XYZ-9999", "ABC-1234"}
                    actual_stolen = set(spotted)
                    if expected_stolen == actual_stolen:
                        state["correct_stolen_plates"] = True
                
                # Check worst hotspot (should be "Mile Marker 42")
                hotspot = data.get("worst_hotspot", "")
                if isinstance(hotspot, str) and hotspot.strip().lower() == "mile marker 42":
                    state["correct_worst_hotspot"] = True

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
