import os
import json
import math

def verify():
    state = {
        "manager_desk_created": False,
        "tip_summary_exists": False,
        "json_format_valid": False,
        "has_correct_keys": False,
        "total_valid_tips_correct": False,
        "boh_hourly_rate_correct": False,
        "foh_hourly_rate_correct": False
    }

    report_path = os.path.join("manager_desk", "tip_summary.json")
    
    if os.path.isdir("manager_desk"):
        state["manager_desk_created"] = True

    if os.path.exists(report_path):
        state["tip_summary_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_format_valid"] = True
            
            required_keys = {"total_valid_tips", "boh_hourly_rate", "foh_hourly_rate"}
            if required_keys.issubset(data.keys()):
                state["has_correct_keys"] = True

                # Expected Math:
                # Valid tips = 3.50 + 2.00 + 0 + 18.00 + 0 + 5.00 + 1.50 + 8.00 = 38.00
                # BOH tip pool = 38.00 * 0.6 = 22.80
                # FOH tip pool = 38.00 * 0.4 = 15.20
                # BOH hours = 150 -> 22.80 / 150 = 0.152
                # FOH hours = 80 -> 15.20 / 80 = 0.190
                
                try:
                    total_tips = float(data["total_valid_tips"])
                    boh_rate = float(data["boh_hourly_rate"])
                    foh_rate = float(data["foh_hourly_rate"])

                    if math.isclose(total_tips, 38.00, abs_tol=0.01):
                        state["total_valid_tips_correct"] = True
                    
                    if math.isclose(boh_rate, 0.152, abs_tol=0.001):
                        state["boh_hourly_rate_correct"] = True
                        
                    if math.isclose(foh_rate, 0.190, abs_tol=0.001):
                        state["foh_hourly_rate_correct"] = True
                except (ValueError, TypeError):
                    pass # Keys exist but values are not castable to float

        except json.JSONDecodeError:
            pass # Invalid JSON format

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
