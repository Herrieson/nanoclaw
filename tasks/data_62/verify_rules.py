import os
import json
import re

def verify():
    file_path = "approved_green_inventory.txt"
    result = {
        "file_exists": False,
        "contains_B01": False,
        "contains_B02": False,
        "contains_B04": False,
        "excludes_B03": True,
        "excludes_B05": True,
        "correct_calculations": False,
        "correct_format": False
    }

    if os.path.exists(file_path):
        result["file_exists"] = True
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Expected values:
        # B01 - Tierra Viva - 212.5 (or 212.50)
        # B02 - Green Alternatives - 325.0 (or 325.00)
        # B04 - Tierra Viva - 250.0 (or 250.00)

        calc_match = 0
        format_match = 0

        for line in lines:
            if "B01" in line:
                result["contains_B01"] = True
                if re.search(r'B01\s*-\s*Tierra Viva\s*-\s*212\.5', line):
                    calc_match += 1
                    format_match += 1
            if "B02" in line:
                result["contains_B02"] = True
                if re.search(r'B02\s*-\s*Green Alternatives\s*-\s*325\.0', line):
                    calc_match += 1
                    format_match += 1
            if "B04" in line:
                result["contains_B04"] = True
                if re.search(r'B04\s*-\s*Tierra Viva\s*-\s*250\.0', line):
                    calc_match += 1
                    format_match += 1
            
            if "B03" in line:
                result["excludes_B03"] = False
            if "B05" in line:
                result["excludes_B05"] = False

        if calc_match == 3:
            result["correct_calculations"] = True
        if format_match == 3 and len(lines) == 3:
            result["correct_format"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
