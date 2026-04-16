import os
import json
import re

def main():
    target_file = "lumber_order.txt"
    result = {
        "file_exists": False,
        "correct_format": False,
        "correct_calculation": False,
        "extracted_value": None
    }

    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                content = f.read().strip()

            # Check format
            if "Total Cedar:" in content and "board feet" in content:
                result["correct_format"] = True

            # Extract the number to see what they got
            match = re.search(r'Total Cedar:\s*([\d\.]+)\s*board feet', content, re.IGNORECASE)
            if match:
                result["extracted_value"] = float(match.group(1))
                
                # Correct calculation:
                # 4 (Bob) + 7 (Alice) + 2 (neighbor) + 5 (Tom) = 18
                # 18 * 2.5 = 45.0
                if result["extracted_value"] == 45.0 or result["extracted_value"] == 45:
                    result["correct_calculation"] = True
        except Exception as e:
            result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    main()
