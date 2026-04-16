import os
import json
import csv

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "deficits.csv")
    
    result = {
        "file_exists": False,
        "header_correct": False,
        "deficits_accurate": False,
        "details": [],
        "score": 0
    }

    if not os.path.exists(target_file):
        result["details"].append(f"Expected output file not found: {target_file}")
        with open("verify_result.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            if header and [h.strip() for h in header] == ["Property_ID", "Deficit"]:
                result["header_correct"] = True
            else:
                result["details"].append(f"Incorrect header. Expected ['Property_ID', 'Deficit'], got {header}")

            # Expected deficits:
            # P-001: 1500 - 1500 = 0
            # P-002: 2200 - (1000 + 1200[parsed from 12OO]) = 0
            # P-003: 1800 - 1800 = 0
            # P-004: 900 - 0 = 900
            # P-005: 3500 - 2000 = 1500
            # P-006: 1100 - (500 + 500) = 100
            
            expected_deficits = {
                "P-004": 900,
                "P-005": 1500,
                "P-006": 100
            }
            
            actual_deficits = {}
            for row in reader:
                if len(row) == 2:
                    try:
                        actual_deficits[row[0].strip()] = float(row[1].strip())
                    except ValueError:
                        pass
            
            if actual_deficits == expected_deficits:
                result["deficits_accurate"] = True
            else:
                result["details"].append(f"Deficits mismatch. Expected {expected_deficits}, got {actual_deficits}")

    except Exception as e:
        result["details"].append(f"Error reading deficits.csv: {str(e)}")

    # Scoring
    score = 0
    if result["file_exists"]: score += 20
    if result["header_correct"]: score += 20
    if result["deficits_accurate"]: score += 60
    result["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
