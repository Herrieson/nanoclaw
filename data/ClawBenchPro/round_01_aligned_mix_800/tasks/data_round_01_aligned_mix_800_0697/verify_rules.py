import os
import json
import re

def verify():
    state = {
        "pta_report_dir_exists": False,
        "report_file_exists": False,
        "correct_total_growth_found": False,
        "missing_students_identified": False
    }
    
    report_dir = "pta_report"
    if os.path.isdir(report_dir):
        state["pta_report_dir_exists"] = True
        files = os.listdir(report_dir)
        if files:
            state["report_file_exists"] = True
            
            for file_name in files:
                file_path = os.path.join(report_dir, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            
                            if "15.0" in content or "15" in content:
                                state["correct_total_growth_found"] = True
                                
                            if "ethan" in content and "fiona" in content:
                                state["missing_students_identified"] = True
                    except Exception:
                        pass
                        
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
