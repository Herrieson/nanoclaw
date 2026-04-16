import os
import json
import csv

def verify():
    report_path = "lab_data/candidates_report.csv"
    state = {
        "report_exists": False,
        "valid_headers": False,
        "rows": [],
        "errors": []
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and set(headers) == {"Batch", "Name", "MW", "Purity"}:
                    state["valid_headers"] = True
                else:
                    state["errors"].append(f"Invalid headers: {headers}")
                
                for row in reader:
                    state["rows"].append(row)
        except Exception as e:
            state["errors"].append(f"Failed to parse CSV: {str(e)}")
            
    # Ground truth calculations:
    # B101: Valid peaks: (4.45, 8000), (2.15, 2000). Total area = 10000.
    # 4.45 matches X. Purity = 8000 / 10000 = 0.8.
    # 2.15 matches Z, but Z has MW -10.0 (invalid). Should be dropped.
    
    # B102: Valid peaks: (5.85, 6000), (8.05, 3000), (1.00, 1000). Total area = 10000.
    # 5.85 matches Y. Purity = 6000 / 10000 = 0.6.
    # 8.05 matches W. Purity = 3000 / 10000 = 0.3.
    # 1.00 has no match.
    
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
