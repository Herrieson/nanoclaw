import os
import json
import re

def verify():
    workspace_dir = "."
    report_file = os.path.join(workspace_dir, "BOLO_report.txt")
    
    state = {
        "report_exists": False,
        "correct_plate": False,
        "correct_location": False,
        "extracted_plate": "",
        "extracted_location": ""
    }

    if os.path.exists(report_file):
        state["report_exists"] = True
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if len(lines) >= 1:
                state["extracted_plate"] = lines[0]
                if "5KTE342" in lines[0].upper():
                    state["correct_plate"] = True
            
            if len(lines) >= 2:
                state["extracted_location"] = lines[1]
                # Target last location is "Warehouse 42, Port District"
                loc = lines[1].upper()
                if "WAREHOUSE 42" in loc and "PORT DISTRICT" in loc:
                    state["correct_location"] = True
        except Exception as e:
            state["error"] = str(e)

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
