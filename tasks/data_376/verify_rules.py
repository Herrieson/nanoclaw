import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "urgent_orders.csv")
    
    state = {
        "csv_exists": False,
        "headers_correct": False,
        "row_count": 0,
        "golden_records_found": 0,
        "decoy_records_found": 0,
        "unexpected_errors": None
    }

    if not os.path.exists(csv_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if headers and [h.strip() for h in headers] == ["job_id", "customer_name", "quantity"]:
                state["headers_correct"] = True
            
            rows = list(reader)
            state["row_count"] = len(rows)

            golden_job_ids = {"9921", "8834", "7712"}
            decoy_job_ids = {"1122", "3344", "5566", "7788"}

            found_golden = 0
            found_decoy = 0

            for row in rows:
                jid = str(row.get("job_id", "")).strip()
                if jid in golden_job_ids:
                    found_golden += 1
                elif jid in decoy_job_ids:
                    found_decoy += 1

            state["golden_records_found"] = found_golden
            state["decoy_records_found"] = found_decoy

    except Exception as e:
        state["unexpected_errors"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
