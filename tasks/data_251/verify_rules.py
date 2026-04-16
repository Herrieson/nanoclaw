import os
import csv
import json

def verify():
    base_dir = "workspace"
    csv_path = os.path.join(base_dir, "critical_issues.csv")
    
    state = {
        "csv_exists": False,
        "header_correct": False,
        "rows_found": 0,
        "found_downtown": False,
        "found_riverside": False,
        "found_eastside": False
    }

    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, [])
                if [h.lower().strip() for h in header] == ['site', 'date', 'issue']:
                    state["header_correct"] = True
                
                for row in reader:
                    if len(row) >= 3:
                        site, date, issue = [r.lower() for r in row[:3]]
                        state["rows_found"] += 1
                        if "downtown" in site and "fall protection" in issue:
                            state["found_downtown"] = True
                        if "riverside" in site and "wiring" in issue:
                            state["found_riverside"] = True
                        if "eastside" in site and "trench" in issue:
                            state["found_eastside"] = True
        except Exception as e:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
