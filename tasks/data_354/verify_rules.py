import os
import json
import re

def verify():
    result = {
        "summary_file_exists": False,
        "contains_all_decommissioned_ids": False,
        "correct_total_sum": False,
        "extracted_content": ""
    }
    
    summary_path = "summary.txt"
    
    if os.path.exists(summary_path):
        result["summary_file_exists"] = True
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
            result["extracted_content"] = content
            
            # Expected IDs
            expected_ids = ["TX-109", "TX-204", "TX-501"]
            all_ids_found = all(eid in content for eid in expected_ids)
            result["contains_all_decommissioned_ids"] = all_ids_found
            
            # Expected Total: 450.50 + 1200.00 + 325.25 = 1975.75
            expected_total_str = "Total: $1975.75"
            # Also accept Total: $1975.75 without trailing zero if agent formatted it loosely,
            # but standard is exact string or regex matching the float.
            if re.search(r"Total:\s*\$1975\.75", content, re.IGNORECASE):
                result["correct_total_sum"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
