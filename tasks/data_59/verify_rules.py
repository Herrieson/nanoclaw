import os
import json
import csv

def verify():
    asset_dir = "."
    target_file = os.path.join(asset_dir, "cleaned_records.csv")
    
    state = {
        "file_exists": False,
        "headers_correct": False,
        "row_count_correct": False,
        "data_correct": False,
        "sorted_correctly": False,
        "dates_standardized": False,
        "audit_applied": False,
        "details": []
    }
    
    if not os.path.exists(target_file):
        state["details"].append("cleaned_records.csv not found.")
        with open(os.path.join(asset_dir, "verify_result.json"), "w") as f:
            json.dump(state, f, indent=4)
        return
        
    state["file_exists"] = True
    
    expected_data = [
        {"PatientID": "1001", "Name": "John Doe", "DiagnosisCode": "J01.91", "VisitDate": "2023-12-05"},
        {"PatientID": "1002", "Name": "Alice Brown-Smith", "DiagnosisCode": "I10", "VisitDate": "2023-11-15"},
        {"PatientID": "1004", "Name": "Charlie Davis", "DiagnosisCode": "K21.9", "VisitDate": "2023-09-01"},
        {"PatientID": "1005", "Name": "Robert Taylor", "DiagnosisCode": "M54.5", "VisitDate": "2023-10-22"},
        {"PatientID": "1006", "Name": "Emily White", "DiagnosisCode": "N39.0", "VisitDate": "2023-12-11"},
        {"PatientID": "1007", "Name": "Frank Miller", "DiagnosisCode": "R51", "VisitDate": "2023-08-30"}
    ]
    
    try:
        with open(target_file, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            if headers == ["PatientID", "Name", "DiagnosisCode", "VisitDate"]:
                state["headers_correct"] = True
            else:
                state["details"].append(f"Incorrect headers: {headers}")
                
            rows = list(reader)
            
            if len(rows) == len(expected_data):
                state["row_count_correct"] = True
            else:
                state["details"].append(f"Expected {len(expected_data)} rows, got {len(rows)}")
                
            # Verify data
            all_correct = True
            dates_ok = True
            audit_ok = True
            sorted_ok = True
            
            prev_id = -1
            
            for i, row in enumerate(rows):
                if i < len(expected_data):
                    exp = expected_data[i]
                    if int(row[0]) < prev_id:
                        sorted_ok = False
                    prev_id = int(row[0])
                    
                    if row[0] != exp["PatientID"]:
                        all_correct = False
                    if row[1] != exp["Name"]:
                        all_correct = False
                        if exp["PatientID"] == "1002": audit_ok = False
                    if row[2] != exp["DiagnosisCode"]:
                        all_correct = False
                        if exp["PatientID"] == "1001": audit_ok = False
                    if row[3] != exp["VisitDate"]:
                        all_correct = False
                        dates_ok = False
                        if exp["PatientID"] == "1006": audit_ok = False
                        
            # Check if 1003 was deleted
            if any(row[0] == "1003" for row in rows):
                audit_ok = False
                all_correct = False
                
            state["data_correct"] = all_correct
            state["sorted_correctly"] = sorted_ok
            state["dates_standardized"] = dates_ok
            state["audit_applied"] = audit_ok
            
    except Exception as e:
        state["details"].append(f"Error parsing CSV: {str(e)}")
        
    with open(os.path.join(asset_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
