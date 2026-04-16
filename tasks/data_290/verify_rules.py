import os
import csv
import json

def verify():
    target_csv = "triage_report.csv"
    result = {
        "csv_exists": False,
        "header_correct": False,
        "row_count_correct": False,
        "data_correct": False,
        "details": []
    }
    
    expected_data = {
        "Pt-1001": {"Systolic": 145, "Diastolic": 90, "Temp": 37.2, "Flagged": "False"},
        "Pt-1002": {"Systolic": 170, "Diastolic": 105, "Temp": 37.0, "Flagged": "True"},
        "Pt-1003": {"Systolic": 120, "Diastolic": 80, "Temp": 36.8, "Flagged": "False"},
        "Pt-1004": {"Systolic": 110, "Diastolic": 70, "Temp": 39.2, "Flagged": "True"},
        "Pt-1005": {"Systolic": 165, "Diastolic": 95, "Temp": 37.1, "Flagged": "True"},
        "Pt-1006": {"Systolic": 130, "Diastolic": 85, "Temp": 38.6, "Flagged": "True"},
        "Pt-1007": {"Systolic": 160, "Diastolic": 100, "Temp": 38.5, "Flagged": "False"}, # Borderline but not strictly > 
    }

    if not os.path.exists(target_csv):
        result["details"].append("CSV file not found.")
    else:
        result["csv_exists"] = True
        try:
            with open(target_csv, 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                expected_headers = ["PatientID", "Systolic", "Diastolic", "Temp", "Flagged"]
                if headers and [h.strip() for h in headers] == expected_headers:
                    result["header_correct"] = True
                else:
                    result["details"].append(f"Headers incorrect. Got: {headers}")

                rows = list(reader)
                if len(rows) == len(expected_data):
                    result["row_count_correct"] = True
                else:
                    result["details"].append(f"Expected {len(expected_data)} rows, got {len(rows)}")

                data_match = True
                for row in rows:
                    pid = row.get("PatientID", "").strip()
                    if pid in expected_data:
                        exp = expected_data[pid]
                        if (float(row.get("Systolic", 0)) != exp["Systolic"] or 
                            float(row.get("Diastolic", 0)) != exp["Diastolic"] or 
                            float(row.get("Temp", 0)) != exp["Temp"] or 
                            str(row.get("Flagged", "")).strip().capitalize() != exp["Flagged"]):
                            data_match = False
                            result["details"].append(f"Data mismatch for {pid}: Got {row}, Expected {exp}")
                    else:
                        data_match = False
                        result["details"].append(f"Unexpected PatientID: {pid}")
                
                result["data_correct"] = data_match and result["row_count_correct"]
        except Exception as e:
            result["details"].append(f"Error reading CSV: {str(e)}")

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
