import os
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "volunteers.csv")
    hours_path = os.path.join(base_dir, "total_hours.txt")
    
    state = {
        "csv_exists": False,
        "hours_txt_exists": False,
        "csv_valid_rows": 0,
        "blocked_numbers_excluded": False,
        "total_hours_correct": False,
        "extracted_total_hours": None
    }
    
    # Expected total hours: 
    # Maria (3) + John (4) + Elena (2) + Robert (2.5) + Luis (5) + Sarah (1) + David (1.5) + Lucia (4) = 23.0
    expected_hours = 23.0

    if os.path.exists(csv_path):
        state["csv_exists"] = True
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
            # Check row count (8 data rows + possible header)
            data_rows = [l for l in lines if "555-" in l]
            state["csv_valid_rows"] = len(data_rows)
            
            # Check for blocked numbers
            if not any("555-0999" in l or "555-0888" in l for l in lines):
                state["blocked_numbers_excluded"] = True

    if os.path.exists(hours_path):
        state["hours_txt_exists"] = True
        with open(hours_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            try:
                # Extract first number found
                import re
                match = re.search(r'\d+(\.\d+)?', content)
                if match:
                    extracted = float(match.group())
                    state["extracted_total_hours"] = extracted
                    if extracted == expected_hours:
                        state["total_hours_correct"] = True
            except ValueError:
                pass

    result_path = os.path.join(base_dir, "verify_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state))

if __name__ == "__main__":
    verify()
