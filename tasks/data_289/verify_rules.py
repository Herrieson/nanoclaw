import os
import json
import re

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "stolen_wages.txt")
    
    result = {
        "file_exists": False,
        "correct_missing_amount": False,
        "correct_hours_mercy": False,
        "correct_hours_oak": False,
        "correct_hours_stjude": False,
        "extracted_first_line": None,
        "raw_content": ""
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            result["raw_content"] = content
            
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        if lines:
            first_line = lines[0]
            result["extracted_first_line"] = first_line
            # The correct missing amount is 402.00 or 402
            # 32 hours * 28.50 = 912
            # 20 hours * 26.00 = 520
            # 24 hours * 30.00 = 720
            # Total = 2152
            # Actual = 1750
            # Missing = 402
            if "402" in first_line:
                result["correct_missing_amount"] = True
                
        # Check hour breakdowns in the remaining content
        content_lower = content.lower()
        if re.search(r'mercy general.*32', content_lower):
            result["correct_hours_mercy"] = True
        if re.search(r'oak creek care.*20', content_lower):
            result["correct_hours_oak"] = True
        if re.search(r'st\.? jude.*24', content_lower):
            result["correct_hours_stjude"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
