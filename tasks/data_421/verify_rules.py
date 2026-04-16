import os
import csv
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "purchase_order.csv")
    
    state = {
        "csv_exists": False,
        "found_parts": [],
        "correct_supplier_codes": False,
        "correct_total": False,
        "total_value_found": None,
        "format_correct": False
    }

    if not os.path.exists(csv_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True

    expected_selections = {
        "MOW-001": "SUP-A2",
        "BLN-202": "SUP-B2",
        "BRG-050": "SUP-C1",
        "SEL-007": "SUP-D1"
    }
    
    expected_total = 75.50

    actual_selections = {}
    actual_total = None
    has_total_row = False

    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            lines = [row for row in reader if any(cell.strip() for cell in row)]
            
            # Simple check if header exists and skip if it does
            if lines and "part" in lines[0][0].lower():
                lines = lines[1:]

            for row in lines:
                if not row: continue
                col0 = row[0].strip().upper()
                
                if "TOTAL" in col0:
                    has_total_row = True
                    try:
                        # Find the first number in the row starting from the end
                        for cell in reversed(row):
                            cell_val = cell.strip().replace('$', '')
                            if cell_val:
                                actual_total = float(cell_val)
                                break
                    except ValueError:
                        pass
                else:
                    if len(row) >= 3:
                        part_id = col0
                        supp_code = row[1].strip()
                        actual_selections[part_id] = supp_code
                        state["found_parts"].append(part_id)
            
            state["total_value_found"] = actual_total
            state["format_correct"] = True
            
            # Check correctness
            all_correct = True
            for pid, expected_code in expected_selections.items():
                if actual_selections.get(pid) != expected_code:
                    all_correct = False
            
            # Ensure no extra parts were ordered
            for pid in actual_selections.keys():
                if pid not in expected_selections:
                    all_correct = False
                    
            state["correct_supplier_codes"] = all_correct
            
            if actual_total is not None and abs(actual_total - expected_total) < 0.01:
                state["correct_total"] = True

    except Exception as e:
        state["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
