import os
import json
import csv

def verify():
    result = {
        "csv_exists": False,
        "csv_valid": False,
        "targets_found": 0,
        "decoys_found": 0,
        "columns_correct": False,
        "exact_match": False
    }

    csv_path = "defibrillators_pre1990.csv"
    
    expected_targets = {"LP4-85-A102", "HS1-89-B991", "ZPD-78-C334"}
    
    if os.path.exists(csv_path):
        result["csv_exists"] = True
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and set(headers) == {"SerialNumber", "Model", "Year"}:
                    result["columns_correct"] = True
                
                found_serials = set()
                for row in reader:
                    sn = row.get("SerialNumber", "").strip()
                    if sn:
                        found_serials.add(sn)
                
                result["csv_valid"] = True
                
                # Check targets
                result["targets_found"] = len(found_serials.intersection(expected_targets))
                # Check decoys (anything not in expected targets is considered a decoy/error)
                result["decoys_found"] = len(found_serials - expected_targets)
                
                if result["targets_found"] == len(expected_targets) and result["decoys_found"] == 0:
                    result["exact_match"] = True
                    
        except Exception as e:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
