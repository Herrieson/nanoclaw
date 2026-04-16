import os
import json
import csv
import re

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "missing_report.csv")
    memo_path = os.path.join(base_dir, "memo.txt")

    result = {
        "report_exists": False,
        "report_headers_correct": False,
        "report_data_accurate": False,
        "memo_exists": False,
        "memo_identifies_culprit": False
    }

    # Verify CSV
    if os.path.exists(report_path):
        result["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and all(h in headers for h in ["Item", "Expected", "Actual", "Discrepancy"]):
                    result["report_headers_correct"] = True
                
                rows = list(reader)
                oxy_correct = False
                add_correct = False
                for row in rows:
                    item = row.get("Item", "").lower()
                    expected = str(row.get("Expected", "")).strip()
                    actual = str(row.get("Actual", "")).strip()
                    diff = str(row.get("Discrepancy", "")).strip()
                    
                    if "oxycodone" in item:
                        if expected == "1500" and actual == "1450" and ("50" in diff or "-50" in diff):
                            oxy_correct = True
                    if "adderall" in item:
                        if expected == "800" and actual == "750" and ("50" in diff or "-50" in diff):
                            add_correct = True
                
                if oxy_correct and add_correct:
                    result["report_data_accurate"] = True
        except Exception:
            pass

    # Verify Memo
    if os.path.exists(memo_path):
        result["memo_exists"] = True
        try:
            with open(memo_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                # John Davis is the only one on shift during the 14:35 delivery
                if "john" in content and "davis" in content:
                    result["memo_identifies_culprit"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
