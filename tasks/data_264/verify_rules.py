import os
import json
import re

def verify():
    base_dir = "."
    summary_file = os.path.join(base_dir, "presentation_summary.md")
    
    result = {
        "summary_file_exists": False,
        "contains_correct_cost": False,
        "contains_top_codes": False,
        "file_content": ""
    }

    if os.path.exists(summary_file):
        result["summary_file_exists"] = True
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            result["file_content"] = content
            
            # Total mins: 120 + 180 = 300 mins = 5 hours.
            # Cost = 5 * 850 = 4250.
            if re.search(r'4,?250(\.00?)?', content):
                result["contains_correct_cost"] = True
            
            # Top codes based on frequency:
            # E-001: 7 events
            # E-002: 6 events
            # E-003: 5 events
            codes_found = 0
            for code in ["E-001", "E-002", "E-003"]:
                if code in content:
                    codes_found += 1
            if codes_found == 3:
                result["contains_top_codes"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
