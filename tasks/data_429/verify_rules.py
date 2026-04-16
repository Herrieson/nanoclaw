import os
import csv
import json

def verify():
    target_file = "vintage_tools/high_hrc_tools.csv"
    result = {
        "file_exists": False,
        "has_correct_headers": False,
        "extracted_tools_correct": False,
        "no_low_hrc": False,
        "score": 0,
        "details": ""
    }

    if not os.path.exists(target_file):
        result["details"] = "The file high_hrc_tools.csv was not found."
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["file_exists"] = True

    try:
        with open(target_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)
            if headers == ['Model', 'HRC', 'Length']:
                result["has_correct_headers"] = True
            
            rows = list(reader)
            extracted_models = [row[0] for row in rows if len(row) >= 1]
            extracted_hrcs = []
            
            for row in rows:
                if len(row) >= 2:
                    try:
                        extracted_hrcs.append(int(row[1]))
                    except ValueError:
                        pass
            
            expected_models = ["Wrench-70A", "Screwdriver-X", "Wrench-72C"]
            not_expected = ["Hammer-B", "Pliers-Q", "Chisel-Old"]

            has_all_expected = all(m in extracted_models for m in expected_models)
            has_no_unexpected = all(m not in extracted_models for m in not_expected)
            
            if has_all_expected:
                result["extracted_tools_correct"] = True
            
            if has_no_unexpected and all(h > 50 for h in extracted_hrcs) and len(extracted_hrcs) == 3:
                result["no_low_hrc"] = True

            score = 20
            if result["has_correct_headers"]: score += 20
            if result["extracted_tools_correct"]: score += 30
            if result["no_low_hrc"]: score += 30
            result["score"] = score
            result["details"] = f"Verification finished. Models found: {extracted_models}"

    except Exception as e:
        result["details"] = f"Error reading CSV: {str(e)}"

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
