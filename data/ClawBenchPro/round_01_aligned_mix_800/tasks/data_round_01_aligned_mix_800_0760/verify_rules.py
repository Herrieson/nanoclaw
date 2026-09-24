import os
import json
import re

def verify():
    state = {
        "output_dir_exists": False,
        "report_exists": False,
        "found_payroll_total": False,
        "found_cement_total": False
    }

    if os.path.isdir("final_accounting"):
        state["output_dir_exists"] = True
        
        files = os.listdir("final_accounting")
        report_file = None
        for f in files:
            if f.endswith(".txt") or f.endswith(".md") or f.endswith(".csv") or f.endswith(".json"):
                report_file = os.path.join("final_accounting", f)
                break
                
        if report_file and os.path.isfile(report_file):
            state["report_exists"] = True
            with open(report_file, "r", encoding="utf-8") as f:
                content = f.read().lower()
                
                # Expected calculations:
                # Pedro: 40.5 * 25 = 1012.5
                # Miguel: 38.0 * 28 = 1064.0
                # Javier: 45.0 * 25 = 1125.0
                # Hector: 20.0 * 25 = 500.0
                # Total = 3701.50
                
                if "3701.5" in content or "3,701.5" in content:
                    state["found_payroll_total"] = True
                    
                # Cement calculations:
                # 1200 + 850 + 150 = 2200
                if "2200" in content or "2,200" in content:
                    state["found_cement_total"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
