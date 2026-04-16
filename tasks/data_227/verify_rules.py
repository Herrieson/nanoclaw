import os
import json
import re

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "wellness_budget.txt")
    
    state = {
        "file_exists": False,
        "line1_correct": False,
        "line2_correct": False,
        "extracted_ids": "",
        "extracted_price": ""
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        with open(target_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if len(lines) >= 2:
            # Expected IDs: 101, 103, 107, 109
            # (101: Seating, 103: Sleep, 107: Seating, 109: Seating)
            # Excluded due to category: 105, 106
            # Excluded due to materials: 102, 104, 108, 110
            # Expected Price: 299.99 + 899.00 + 85.00 + 350.00 = 1633.99
            
            # Clean up line 1 to just digits
            actual_ids = re.findall(r'\d+', lines[0])
            state["extracted_ids"] = ", ".join(actual_ids)
            
            if actual_ids == ["101", "103", "107", "109"]:
                state["line1_correct"] = True
                
            actual_price_match = re.search(r'\d+\.\d{2}', lines[1])
            if actual_price_match:
                state["extracted_price"] = actual_price_match.group(0)
                if state["extracted_price"] == "1633.99":
                    state["line2_correct"] = True

    # Output verification state
    result_path = os.path.join(base_dir, "verify_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
