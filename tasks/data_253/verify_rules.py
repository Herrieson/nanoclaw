import os
import json
import re

def verify():
    report_file = "claim_report.txt"
    result = {
        "report_exists": False,
        "total_shortage_correct": False,
        "workers_correct": False,
        "lawyer_name_correct": False,
        "lawyer_email_correct": False
    }

    if not os.path.exists(report_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["report_exists"] = True
    
    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read().lower()

    # Total shortage should be 450
    if "450" in content:
        result["total_shortage_correct"] = True

    # Workers should include miguel, carlos, hector
    if all(w in content for w in ["miguel", "carlos", "hector"]):
        result["workers_correct"] = True

    # Lawyer Name
    if "sofia ramirez" in content:
        result["lawyer_name_correct"] = True

    # Lawyer Email
    if "s.ramirez@workersjustice-mock.org" in content:
        result["lawyer_email_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
