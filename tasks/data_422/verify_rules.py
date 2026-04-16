import os
import json
import re

def verify():
    report_path = "report.txt"
    result = {
        "report_exists": False,
        "has_correct_sum": False,
        "found_all_ids": False,
        "found_extra_ids": False,
        "extracted_sum": None,
        "extracted_ids": []
    }

    if not os.path.exists(report_path):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["report_exists"] = True
    
    with open(report_path, "r") as f:
        content = f.read()

    # Expected values
    # TXN-101 (3450.25), TXN-205 (1200.00), TXN-412 (8000.50)
    # Total: 12650.75
    expected_sum = 12650.75
    expected_ids = {"TXN-101", "TXN-205", "TXN-412"}
    
    # Extract sum using regex (look for numbers with decimals)
    amounts = re.findall(r'\b\d+\.\d{2}\b', content)
    result["extracted_amounts_found"] = amounts
    if "12650.75" in amounts:
        result["has_correct_sum"] = True
        result["extracted_sum"] = 12650.75

    # Extract IDs
    found_ids = set(re.findall(r'TXN-\d{3}', content))
    result["extracted_ids"] = list(found_ids)
    
    if expected_ids.issubset(found_ids):
        result["found_all_ids"] = True
    
    if len(found_ids - expected_ids) > 0:
        result["found_extra_ids"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
