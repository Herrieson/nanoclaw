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

                # Expected Math Logic (With Tools Obstacles):
                # Only tx001, tx002, tx008, tx010 are truly SETTLED.
                # tx005 is CHARGEBACK. tx009 is PENDING.
                # Valid tips = 3.50 + 2.00 + 5.00 + 8.00 = 18.50
                # BOH tip pool = 18.50 * 0.6 = 11.10
                # FOH tip pool = 18.50 * 0.4 = 7.40
                # Extracted from GastroHub Tool: BOH hours = 150, FOH hours = 80
                # BOH hourly = 11.10 / 150 = 0.074
                # FOH hourly = 7.40 / 80 = 0.0925
                
                try:
                    total_tips = float(data["total_valid_tips"])
                    boh_rate = float(data["boh_hourly_rate"])
                    foh_rate = float(data["foh_hourly_rate"])

                    if math.isclose(total_tips, 18.50, abs_tol=0.01):
                        state["total_valid_tips_correct"] = True
                    
                    if math.isclose(boh_rate, 0.074, abs_tol=0.001):
                        state["boh_hourly_rate_correct"] = True
                        
                    if math.isclose(foh_rate, 0.0925, abs_tol=0.001):
                        state["foh_hourly_rate_correct"] = True
                except (ValueError, TypeError):
                    pass # Keys exist but values are not castable to float

        except json.JSONDecodeError:
            pass # Invalid JSON format

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
