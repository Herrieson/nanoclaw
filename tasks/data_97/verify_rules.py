import os
import json
import csv

def verify():
    workspace_dir = '.'
    success_csv_path = os.path.join(workspace_dir, 'successful_readings.csv')
    failed_csv_path = os.path.join(workspace_dir, 'failed_access.csv')

    state = {
        "success_file_exists": False,
        "failed_file_exists": False,
        "success_header_correct": False,
        "failed_header_correct": False,
        "success_data_count": 0,
        "failed_data_count": 0,
        "usage_calculations_correct": False,
        "failed_reasons_correct": False
    }

    if os.path.exists(success_csv_path):
        state["success_file_exists"] = True
        try:
            with open(success_csv_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                header = [h.strip() for h in header]
                if header == ['Address', 'Meter_ID', 'Current_Reading', 'Usage']:
                    state["success_header_correct"] = True
                
                rows = list(reader)
                state["success_data_count"] = len(rows)

                # Check calculations
                # A-1002: 5520 - 5400 = 120
                # A-1003: 12450 - 12200 = 250
                # B-2055: 450 - 350 = 100
                # C-3010: 99800 - 99100 = 700
                # C-3012: 1050 - 950 = 100
                expected_usages = {
                    "A-1002": 120,
                    "A-1003": 250,
                    "B-2055": 100,
                    "C-3010": 700,
                    "C-3012": 100
                }
                
                correct_calcs = 0
                for row in rows:
                    if len(row) == 4:
                        meter_id = row[1].strip()
                        usage = int(row[3].strip())
                        if meter_id in expected_usages and expected_usages[meter_id] == usage:
                            correct_calcs += 1
                
                if correct_calcs == 5 and len(rows) == 5:
                    state["usage_calculations_correct"] = True

        except Exception as e:
            pass

    if os.path.exists(failed_csv_path):
        state["failed_file_exists"] = True
        try:
            with open(failed_csv_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                header = [h.strip() for h in header]
                if header == ['Address', 'Meter_ID', 'Reason']:
                    state["failed_header_correct"] = True
                
                rows = list(reader)
                state["failed_data_count"] = len(rows)

                expected_reasons = {
                    "A-1004": "LOCKED_GATE",
                    "B-2056": "VICIOUS_DOG",
                    "C-3011": "METER_BURIED"
                }

                correct_reasons = 0
                for row in rows:
                    if len(row) == 3:
                        meter_id = row[1].strip()
                        reason = row[2].strip()
                        if meter_id in expected_reasons and expected_reasons[meter_id] == reason:
                            correct_reasons += 1
                
                if correct_reasons == 3 and len(rows) == 3:
                    state["failed_reasons_correct"] = True

        except Exception as e:
            pass

    with open(os.path.join(workspace_dir, 'verify_result.json'), 'w') as f:
        json.dump(state, f, indent=4)

if __name__ == '__main__':
    verify()
