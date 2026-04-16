import os
import json
import math

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "fairness_report.json")
    
    result = {
        "report_exists": False,
        "valid_json": False,
        "group_a_correct": False,
        "group_b_correct": False,
        "group_c_correct": False
    }

    if not os.path.exists(report_path):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["report_exists"] = True

    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        result["valid_json"] = True
    except:
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    # Expected calculations based on formula:
    # adjusted = base - (cred/1000) + (50000/inc)
    
    # Group A
    # A001: 0.5 - 0.6 + 2.0 = 1.9
    # A002: 0.2 - 0.75 + 0.5 = -0.05
    # Avg A = (1.9 + -0.05) / 2 = 0.925
    
    # Group B
    # A003: 0.4 - 0.65 + 1.0 = 0.75
    # A004: 0.45 - 0.62 + 1.25 = 1.08
    # Avg B = (0.75 + 1.08) / 2 = 0.915
    
    # Group C
    # A005: 0.3 - 0.71 + 0.625 = 0.215
    # A006: 0.55 - 0.58 + 1.666666... = 1.636666...
    # Avg C = (0.215 + 1.636666...) / 2 = 0.9258333...

    val_a = data.get("Group_A")
    val_b = data.get("Group_B")
    val_c = data.get("Group_C")

    if val_a is not None and math.isclose(val_a, 0.925, rel_tol=1e-3):
        result["group_a_correct"] = True
    if val_b is not None and math.isclose(val_b, 0.915, rel_tol=1e-3):
        result["group_b_correct"] = True
    if val_c is not None and math.isclose(val_c, 0.9258333, rel_tol=1e-3):
        result["group_c_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
