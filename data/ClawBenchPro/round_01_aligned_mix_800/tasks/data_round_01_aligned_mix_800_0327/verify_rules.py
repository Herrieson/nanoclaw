import os
import sys
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "boss_report.txt")
    
    state = {
        "report_exists": False,
        "found_car_A": False,
        "found_car_C": False,
        "found_car_D": False,
        "excluded_car_B": True,
        "correct_spark_plugs": False
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read().upper()
            
            # Urgent plates: ABC-123 (Misfire), LMN-456 (Catalyst), QRS-111 (Both)
            if "ABC-123" in content:
                state["found_car_A"] = True
            if "LMN-456" in content:
                state["found_car_C"] = True
            if "QRS-111" in content:
                state["found_car_D"] = True
                
            # Non-urgent plate: XYZ-987 (Should NOT be in the report)
            if "XYZ-987" in content:
                state["excluded_car_B"] = False
                
            # Spark plugs count check (NGK-9981 = 12, BOSCH-9669 = 8 -> Total 20)
            if re.search(r'\b20\b', content):
                state["correct_spark_plugs"] = True

    state_out = os.path.join(workspace, "state.json")
    with open(state_out, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
