import os
import csv
import json
import subprocess

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "medicaid_j_codes.csv")
    script_path = os.path.join(base_dir, "send_report.py")
    
    state = {
        "csv_exists": False,
        "csv_headers_correct": False,
        "csv_rows_count": 0,
        "csv_data_correct": False,
        "script_execution_success": False,
        "script_output": "",
        "script_output_correct": False
    }

    expected_claim_ids = set(["C1001", "C1005", "C1022", "C1033"])
    expected_sum = 450.75 + 150.25 + 80.50 + 120.00
    
    # Check CSV from the random seed + targets
    # We generated targets explicitly, plus random ones
    # Let's dynamically calculate expected from the raw file just to be absolutely safe
    raw_path = os.path.join(base_dir, "raw_claims", "claims_dump_2023.txt")
    true_expected_ids = set()
    true_expected_sum = 0.0
    
    if os.path.exists(raw_path):
        with open(raw_path, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 6:
                    cid, pid, prov, diag, amt, date = parts
                    if prov == 'Medicaid' and diag.startswith('J'):
                        true_expected_ids.add(cid)
                        true_expected_sum += float(amt.replace('$', ''))

    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                if headers == ["claim_id", "patient_id", "amount"]:
                    state["csv_headers_correct"] = True
                
                extracted_ids = set()
                data_clean = True
                for row in reader:
                    if len(row) == 3:
                        extracted_ids.add(row[0])
                        if '$' in row[2]:
                            data_clean = False
                            
                state["csv_rows_count"] = len(extracted_ids)
                if extracted_ids == true_expected_ids and data_clean:
                    state["csv_data_correct"] = True
        except Exception as e:
            pass

    # Check script execution
    if os.path.exists(script_path):
        try:
            result = subprocess.run(["python3", script_path], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                state["script_execution_success"] = True
                out = result.stdout.strip()
                state["script_output"] = out
                
                # Check if output is ONLY the float number
                try:
                    out_val = float(out)
                    if abs(out_val - true_expected_sum) < 0.01 and str(out_val) == out or f"{out_val:.2f}" == out or out.replace('.','',1).isdigit():
                        state["script_output_correct"] = True
                except ValueError:
                    state["script_output_correct"] = False
        except Exception as e:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
