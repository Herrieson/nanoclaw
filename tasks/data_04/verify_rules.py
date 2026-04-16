import os
import json
import csv

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "defect_report.csv")
    truth_path = os.path.join(base_dir, ".ground_truth.json")
    
    state = {
        "report_exists": False,
        "valid_csv": False,
        "total_defects_found": 0,
        "expected_defects_count": 0,
        "dates_standardized": False,
        "all_records_match": False,
        "errors": []
    }

    if not os.path.exists(truth_path):
        state["errors"].append("Ground truth file missing, environment corrupted.")
        return state

    with open(truth_path, 'r') as f:
        expected_defects = json.load(f)
    
    state["expected_defects_count"] = len(expected_defects)

    if not os.path.exists(report_path):
        state["errors"].append("defect_report.csv not found.")
        return state
        
    state["report_exists"] = True

    try:
        with open(report_path, 'r') as f:
            # Sniff dialect and check if it has a header
            sample = f.read(1024)
            f.seek(0)
            
            reader = csv.reader(f)
            rows = list(reader)
            
            if len(rows) == 0:
                state["errors"].append("CSV is empty.")
                return state
                
            state["valid_csv"] = True
            
            # Check if first row is a header
            data_rows = rows
            if "date" in rows[0][0].lower():
                data_rows = rows[1:]
                
            state["total_defects_found"] = len(data_rows)
            
            # Verify dates and content
            dates_ok = True
            matched_records = 0
            
            expected_tuples = set((d["date"], d["machine"], d["reason"]) for d in expected_defects)
            found_tuples = set()
            
            for row in data_rows:
                if len(row) >= 3:
                    date_val, machine_val, reason_val = row[0].strip(), row[1].strip(), row[2].strip()
                    found_tuples.add((date_val, machine_val, reason_val))
                    
                    # Check date format YYYY-MM-DD
                    if len(date_val) != 10 or date_val[4] != '-' or date_val[7] != '-':
                        dates_ok = False
            
            state["dates_standardized"] = dates_ok
            
            missing = expected_tuples - found_tuples
            extra = found_tuples - expected_tuples
            
            if len(missing) == 0 and len(extra) == 0:
                state["all_records_match"] = True
            else:
                state["errors"].append(f"Missing {len(missing)} records, found {len(extra)} extra/malformed records.")

    except Exception as e:
        state["errors"].append(f"Error parsing CSV: {str(e)}")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
    with open("verify_result.json", "r") as f:
        print(f.read())
