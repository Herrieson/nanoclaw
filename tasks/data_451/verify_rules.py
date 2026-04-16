import os
import csv
import json
import re

def verify():
    target_dir = "."
    csv_path = os.path.join(target_dir, "saw_import.csv")
    boards_path = os.path.join(target_dir, "boards_needed.txt")
    
    state = {
        "has_csv": False,
        "csv_headers_correct": False,
        "csv_row_count": 0,
        "csv_mm_accurate": False,
        "has_boards_needed": False,
        "boards_needed_value": None
    }
    
    # 1. Check CSV
    if os.path.exists(csv_path):
        state["has_csv"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                if len(headers) >= 3 and headers[0].strip() == "CutID" and headers[1].strip() == "Length_mm" and headers[2].strip() == "Material":
                    state["csv_headers_correct"] = True
                
                rows = list(reader)
                state["csv_row_count"] = len(rows)
                
                # Verify MM conversion accuracy (34.5 in = 876.3 mm)
                # Let's sample the rows to see if 876.3 (or close) is in there
                mm_values = []
                for row in rows:
                    if len(row) >= 2:
                        try:
                            val = float(re.sub(r'[^\d\.]', '', row[1]))
                            mm_values.append(val)
                        except ValueError:
                            pass
                
                # 34.5 * 25.4 = 876.3
                # 40 * 25.4 = 1016.0
                if any(abs(v - 876.3) < 1.0 for v in mm_values) and any(abs(v - 1016.0) < 1.0 for v in mm_values):
                    state["csv_mm_accurate"] = True

        except Exception as e:
            pass

    # 2. Check Boards Needed
    if os.path.exists(boards_path):
        state["has_boards_needed"] = True
        try:
            with open(boards_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                # Find the first integer
                match = re.search(r'\d+', content)
                if match:
                    state["boards_needed_value"] = int(match.group())
        except Exception:
            pass

    # Write out verification state
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
