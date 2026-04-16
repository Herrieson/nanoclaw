import os
import json
import re

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "krakow_summary.txt")
    
    result = {
        "file_exists": False,
        "total_correct": False,
        "parts_listed": False,
        "found_total": None
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        with open(target_file, 'r') as f:
            content = f.read()
            
            # Check if all KP parts are mentioned
            parts = ["KP-001", "KP-002", "KP-003", "KP-004"]
            all_parts_found = all(part in content for part in parts)
            result["parts_listed"] = all_parts_found
            
            # Extract total value
            # Look for Total: 1100 or Total: $1100.00 etc
            match = re.search(r'Total:\s*\$?(\d+\.?\d*)', content, re.IGNORECASE)
            if match:
                total_val = float(match.group(1))
                result["found_total"] = total_val
                if abs(total_val - 1100.00) < 0.01:
                    result["total_correct"] = True

    with open(os.path.join(base_dir, "verify_result.json"), 'w') as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
