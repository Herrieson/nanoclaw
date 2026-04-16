import os
import json
import re

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "maintenance_report.txt")
    
    state = {
        "report_exists": False,
        "total_downtime_correct": False,
        "most_frequent_component_correct": False,
        "unique_error_codes_correct": False,
        "extracted_downtime": None,
        "extracted_component": None,
        "extracted_codes": None
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Expected values:
            # Downtime: 45 + 120 + 60 + 30 + 40 + 15 + 90 = 400
            # Component: Tension_Belt (4 occurrences vs Spindle_A's 2 and Extruder_Valve's 1)
            # Codes: EW-404, EW-102, EW-505, EW-103
            
            downtime_match = re.search(r'\*\*Total Downtime \(minutes\):\*\*\s*(\d+)', content, re.IGNORECASE)
            if downtime_match:
                state["extracted_downtime"] = downtime_match.group(1)
                if state["extracted_downtime"] == "400":
                    state["total_downtime_correct"] = True
            
            component_match = re.search(r'\*\*Most Frequent Failing Component:\*\*\s*([A-Za-z0-9_]+)', content, re.IGNORECASE)
            if component_match:
                state["extracted_component"] = component_match.group(1)
                if state["extracted_component"].lower() == "tension_belt":
                    state["most_frequent_component_correct"] = True
                    
            codes_match = re.search(r'\*\*Unique Error Codes:\*\*\s*(.*)', content, re.IGNORECASE)
            if codes_match:
                state["extracted_codes"] = codes_match.group(1)
                codes = [c.strip().upper() for c in re.split(r'[,| ]+', state["extracted_codes"]) if c.strip()]
                expected_codes = {"EW-404", "EW-102", "EW-505", "EW-103"}
                if expected_codes.issubset(set(codes)) and len(set(codes) - expected_codes) == 0:
                    state["unique_error_codes_correct"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
