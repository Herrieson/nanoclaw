import os
import csv
import json

def verify():
    target_file = "rejected_summary.csv"
    state = {
        "file_exists": False,
        "format_correct": False,
        "patients_found": [],
        "total_calculated": None,
        "is_total_correct": False
    }

    expected_patients = ["P-1001", "P-2034", "P-5521", "P-1122"]
    expected_total = 1500.00 + 320.50 + 899.99 + 100.00 # 2820.49

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, 'r', newline='') as f:
                # Basic sniff to see if it has headers or not, let's just read rows
                reader = csv.reader(f)
                rows = list(reader)
                
                # Filter out empty rows
                rows = [r for r in rows if len(r) >= 2]

                if rows:
                    # Check if last row is total
                    last_row = rows[-1]
                    if last_row[0].strip().lower() == "total":
                        try:
                            state["total_calculated"] = float(last_row[1].strip())
                            if abs(state["total_calculated"] - expected_total) < 0.01:
                                state["is_total_correct"] = True
                        except ValueError:
                            pass
                    
                    # Extract patients
                    for r in rows:
                        pid = r[0].strip()
                        if pid.startswith("P-"):
                            state["patients_found"].append(pid)
                    
                    # Check if all expected patients are in the found list
                    missing = [p for p in expected_patients if p not in state["patients_found"]]
                    if not missing:
                        state["format_correct"] = True

        except Exception as e:
            state["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
