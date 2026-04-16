import os
import re

def verify():
    results = {
        "repair_plan_exists": False,
        "correct_vin_found": False,
        "correct_error_code": False,
        "avg_voltage_calculated": False,
        "fix_identified": False
    }
    
    plan_path = "repair_plan.txt"
    if os.path.exists(plan_path):
        results["repair_plan_exists"] = True
        with open(plan_path, "r") as f:
            content = f.read().upper()
            
            if "1B74VINTAGEREST01" in content:
                results["correct_vin_found"] = True
            
            if "P0171" in content:
                results["correct_error_code"] = True
                
            if "VACUUM LEAK" in content or "INTAKE MANIFOLD" in content:
                results["fix_identified"] = True
            
            # Check for average voltage calculation (approx 0.175)
            # We look for a number between 0.1 and 0.3
            voltages = re.findall(r"0\.\d+", content)
            for v in voltages:
                if 0.1 <= float(v) <= 0.3:
                    results["avg_voltage_calculated"] = True
                    break

    # Output for LLM judge
    import json
    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
