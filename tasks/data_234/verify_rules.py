import os
import json
import re

def verify():
    report_path = "buck_report.txt"
    state = {
        "report_exists": False,
        "target_1_found": False,
        "target_2_found": False,
        "extra_data_present": False,
        "format_correct": False
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r") as f:
            content = f.read()
            
            # Check for Target 1: 2023-11-05 05:45:00, Temp: 28F
            if re.search(r"2023-11-05\s+05:45:00\s*-\s*Temp:\s*28F", content, re.IGNORECASE):
                state["target_1_found"] = True
                
            # Check for Target 2: 2023-11-06 17:30:00, Temp: 31F
            if re.search(r"2023-11-06\s+17:30:00\s*-\s*Temp:\s*31F", content, re.IGNORECASE):
                state["target_2_found"] = True
                
            # Check for incorrect data (Squirrel, Turkey, Doe, Raccoon)
            if re.search(r"(Squirrel|Turkey|Doe|Raccoon)", content, re.IGNORECASE):
                state["extra_data_present"] = True
                
            # Check strict formatting
            lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
            valid_format = all(re.match(r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s-\sTemp:\s\d+F$", line) for line in lines)
            if valid_format and len(lines) == 2:
                state["format_correct"] = True
                
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)
        
if __name__ == "__main__":
    verify()
