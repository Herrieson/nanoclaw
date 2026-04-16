import os
import csv
import json
import re

def verify():
    results = {
        "final_file_exists": False,
        "record_count_correct": False,
        "column_shift_fixed": False,
        "base64_decoded": False,
        "ssn_format_valid": False,
        "sorted_correctly": False,
        "audit_report_exists": False
    }
    
    target_path = "sanitized/final_patient_records_2023.csv"
    audit_path = "sanitized/audit_summary.json"
    
    if os.path.exists(target_path):
        results["final_file_exists"] = True
        with open(target_path, 'r') as f:
            reader = list(csv.DictReader(f))
            results["record_count_correct"] = (len(reader) == 40)
            
            # Check for column shift fix (look for Patient_1021 to 1030)
            shifted_sample = [r for r in reader if r['Patient_ID'] in [f"P-{i}" for i in range(1021, 1031)]]
            if shifted_sample:
                # SSN should match \d{3}-\d{2}-\d{4}
                results["column_shift_fixed"] = all(re.match(r'^\d{3}-\d{2}-\d{4}$', r['SSN']) for r in shifted_sample)
            
            # Check Base64 decoding
            encoded_sample = [r for r in reader if r['Patient_ID'] == "P-1035"][0]
            if "Critical condition" in encoded_sample['Treatment_Notes']:
                results["base64_decoded"] = True
            
            # Check all SSN formats
            results["ssn_format_valid"] = all(re.match(r'^\d{3}-\d{2}-\d{4}$', r['SSN']) for r in reader)
            
            # Check sorting
            ids = [int(r['Patient_ID'].split('-')[1]) for r in reader]
            results["sorted_correctly"] = (ids == sorted(ids))

    if os.path.exists(audit_path):
        results["audit_report_exists"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
