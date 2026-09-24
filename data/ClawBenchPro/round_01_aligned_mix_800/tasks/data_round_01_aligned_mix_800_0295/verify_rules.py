import os
import json

def verify():
    results = {
        "payroll_json_exists": False,
        "audit_summary_exists": False,
        "ghost_employee_identified": False,
        "overtime_limit_violation_found": False,
        "math_accuracy_and_payout_calculated": False,
        "names_fetched_from_api": False
    }

    payroll_path = "deliverables/payroll_final.json"
    summary_path = "deliverables/audit_summary.txt"

    if os.path.exists(payroll_path):
        results["payroll_json_exists"] = True
        try:
            with open(payroll_path, "r") as f:
                data = json.load(f)
                ids = [item.get("id") or item.get("employee_id") for item in data]
                
                # Ghost E004 should be excluded, white-listed E001/E002 should be included
                if "E004" not in ids and any(x in ids for x in ["E001", "E002"]):
                    # Check if total payout and hourly rate were calculated correctly
                    for item in data:
                        if "hourly_rate" in item and ("payout" in item or "total_payout" in item or "total_pay" in item):
                            results["math_accuracy_and_payout_calculated"] = True
                        if "name" in item and item["name"].lower() not in ["", "unknown"]:
                            results["names_fetched_from_api"] = True
        except:
            pass

    if os.path.exists(summary_path):
        results["audit_summary_exists"] = True
        with open(summary_path, "r") as f:
            content = f.read().lower()
            # E004 Dave is ghost
            if "dave" in content or "e004" in content:
                results["ghost_employee_identified"] = True
            # E002 Bob exceeded overtime
            if "bob" in content or "e002" in content:
                results["overtime_limit_violation_found"] = True

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
