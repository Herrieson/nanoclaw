import os
import json
import re

def verify():
    base_dir = "."
    order_file = os.path.join(base_dir, "order_form.txt")
    
    result = {
        "order_form_exists": False,
        "missing_parts_found": [],
        "extra_parts_found": [],
        "total_cost_found": None,
        "is_total_correct": False,
        "expected_total": "33.99",
        "expected_missing": ["P002", "P004", "P006", "P008", "P009", "P011", "P012", "P013", "P014", "P016", "P017", "P020"]
    }

    if os.path.exists(order_file):
        result["order_form_exists"] = True
        with open(order_file, "r") as f:
            content = f.read()
            
        # Find parts in the file
        parts_in_file = re.findall(r"P\d{3}", content)
        
        # Check against expected
        result["missing_parts_found"] = [p for p in result["expected_missing"] if p in parts_in_file]
        result["extra_parts_found"] = [p for p in parts_in_file if p not in result["expected_missing"]]
        
        # Find total cost
        total_match = re.search(r"Total:\s*\$([0-9]+\.[0-9]{2})", content)
        if total_match:
            result["total_cost_found"] = total_match.group(1)
            if result["total_cost_found"] == result["expected_total"]:
                result["is_total_correct"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
