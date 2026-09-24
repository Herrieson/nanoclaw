import os
import json
import re

def verify():
    results = {
        "payroll_json_exists": False,
        "audit_summary_exists": False,
        "ghost_employee_identified": False,
        "overtime_limit_violation_found": False,
        "math_accuracy": False
    }

    payroll_path = "deliverables/payroll_final.json"
    summary_path = "deliverables/audit_summary.txt"

    # Check file existence
    if os.path.exists(payroll_path):
        results["payroll_json_exists"] = True
        try:
            with open(payroll_path, "r") as f:
                data = json.load(f)
                # Check if Dave (Ghost) is NOT in the final clean payroll
                # and if Alice/Bob/Charlie/Eve are handled
                ids = [item.get("id") or item.get("employee_id") for item in data]
                if "E004" not in ids and any(x in ids for x in ["E001", "E002"]):
                    results["math_accuracy"] = True
        except:
            pass

    if os.path.exists(summary_path):
        results["audit_summary_exists"] = True
        with open(summary_path, "r") as f:
            content = f.read().lower()
            # Check for Ghost employee Dave
            if "dave" in content or "e004" in content:
                results["ghost_employee_identified"] = True
            # Check for Bob who exceeded 10% (Scheduled 20, Logged 25)
            if "bob" in content or "e002" in content:
                results["overtime_limit_violation_found"] = True

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
