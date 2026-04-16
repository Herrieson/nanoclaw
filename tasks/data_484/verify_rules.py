import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "order_sheet.csv")
    
    state = {
        "csv_exists": False,
        "header_correct": False,
        "row_count_correct": False,
        "data_correct": False,
        "sorted_correctly": False,
        "error_msg": ""
    }
    
    if not os.path.exists(csv_path):
        state["error_msg"] = "order_sheet.csv not found."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True
    
    expected_data = [
        {"Part_ID": "SUS-404", "Part_Name": "Coilover Shock Absorber", "Price": 420.00 * 0.85}, # 357.00
        {"Part_ID": "MNT-001", "Part_Name": "Engine Mount Bracket", "Price": 65.00 * 0.85},   # 55.25
        {"Part_ID": "FRM-88X", "Part_Name": "Tubular Frame Gusset", "Price": 45.00 * 0.85}    # 38.25
    ]
    # Already sorted descending by discounted price: 357.00, 55.25, 38.25

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            
            if not reader:
                state["error_msg"] = "CSV is empty."
                raise ValueError()
                
            header = reader[0]
            if header == ["Part_ID", "Part_Name", "Discounted_Price"]:
                state["header_correct"] = True
                
            rows = reader[1:]
            if len(rows) == 3:
                state["row_count_correct"] = True
            
            parsed_rows = []
            for r in rows:
                if len(r) == 3:
                    parsed_rows.append({"Part_ID": r[0], "Part_Name": r[1], "Discounted_Price": float(r[2])})
            
            # Check data correctness and sorting
            if len(parsed_rows) == 3:
                matches = 0
                for i, exp in enumerate(expected_data):
                    actual = parsed_rows[i]
                    if actual["Part_ID"] == exp["Part_ID"] and \
                       actual["Part_Name"] == exp["Part_Name"] and \
                       abs(actual["Discounted_Price"] - exp["Price"]) < 0.01:
                        matches += 1
                
                if matches == 3:
                    state["data_correct"] = True
                    state["sorted_correctly"] = True
                else:
                    # Maybe correct data but wrong sort
                    ids = [r["Part_ID"] for r in parsed_rows]
                    if set(ids) == {"SUS-404", "MNT-001", "FRM-88X"}:
                        state["data_correct"] = True # Data is there but unsorted or slightly wrong math
                        
    except Exception as e:
        state["error_msg"] = f"Error parsing CSV: {str(e)}"
        
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
