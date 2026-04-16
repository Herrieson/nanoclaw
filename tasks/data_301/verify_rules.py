import os
import json
import csv

def verify():
    base_dir = "."
    state = {
        "csv_exists": False,
        "csv_headers_correct": False,
        "csv_rows_correct": False,
        "txt_exists": False,
        "total_value_correct": False
    }
    
    csv_path = os.path.join(base_dir, "appraised_french_items.csv")
    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if headers and [h.strip() for h in headers] == ["Item_ID", "Name", "Condition", "Value"]:
                    state["csv_headers_correct"] = True
                    
                rows = list(reader)
                if len(rows) == 3:
                    ids = set(r.get("Item_ID", "").strip() for r in rows)
                    try:
                        values = set(float(r.get("Value", "0").strip()) for r in rows)
                    except ValueError:
                        values = set()
                        
                    if ids == {"A1", "A3", "A4"} and values == {150.0, 85.0, 40.0}:
                        state["csv_rows_correct"] = True
        except Exception:
            pass
            
    txt_path = os.path.join(base_dir, "total_value.txt")
    if os.path.exists(txt_path):
        state["txt_exists"] = True
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if "275" in content:
                    state["total_value_correct"] = True
        except Exception:
            pass
            
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
