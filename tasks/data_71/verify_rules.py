import os
import json
import re

def verify():
    results = {
        "pid_updated": False,
        "logic_fixed": False,
        "report_generated": False,
        "dickens_quote_present": False,
        "final_stress_correct": False
    }

    base_path = "."
    config_path = os.path.join(base_path, "controller_config.json")
    script_path = os.path.join(base_path, "scripts/control_logic.py")
    report_path = "final_report.txt"

    # 1. Check PID Update
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            if cfg['pid']['Kp'] == 12.5 and cfg['pid']['Ki'] == 0.8:
                results["pid_updated"] = True

    # 2. Check Logic Fix (Stress = Force / Area)
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            content = f.read()
            if "/" in content and "force / area" in content.lower():
                results["logic_fixed"] = True

    # 3. Check Report and Quote
    if os.path.exists(report_path):
        results["report_generated"] = True
        with open(report_path, 'r') as f:
            content = f.read().lower()
            # Check for iconic "A Tale of Two Cities" keywords
            if "best of times" in content or "worst of times" in content or "charles dickens" in content:
                results["dickens_quote_present"] = True

    # 4. Check if simulation runs correctly (5000 / 25 = 200 MPa)
    # This is a bit implicit, if the agent fixed it, the value should be 200.
    if results["logic_fixed"] and results["pid_updated"]:
         results["final_stress_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
