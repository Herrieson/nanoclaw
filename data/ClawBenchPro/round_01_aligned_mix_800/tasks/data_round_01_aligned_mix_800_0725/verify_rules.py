import os
import json
import re

def verify():
    results = {
        "unauthorized_report_exists": False,
        "final_audit_exists": False,
        "blacklisted_intruders_correct": False,
        "mary_hours_correct": False,
        "total_volunteers_counted": 0,
        "json_format_valid": False
    }

    report_path = "deliverables/unauthorized_report.txt"
    audit_path = "deliverables/final_audit.json"

    # Check existence
    if os.path.exists(report_path):
        results["unauthorized_report_exists"] = True
        with open(report_path, "r") as f:
            content = f.read().lower()
            if "intruder dave" in content and "evil steve" in content:
                results["blacklisted_intruders_correct"] = True

    if os.path.exists(audit_path):
        results["final_audit_exists"] = True
        try:
            with open(audit_path, "r") as f:
                data = json.load(f)
                results["json_format_valid"] = True
                results["total_volunteers_counted"] = len(data)
                
                # Math check: Mary = 3.5 (w1) + 2.5 (w2) + 1.0 (notes) = 7.0
                mary_hours = data.get("Mary Sobieski", 0)
                if abs(float(mary_hours) - 7.0) < 0.1:
                    results["mary_hours_correct"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
