import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "shopping_list.csv")
    
    state = {
        "file_exists": False,
        "has_header": False,
        "items_found": [],
        "is_correct": False,
        "error_msg": ""
    }
    
    expected_data = {
        "Hemp Canvas": {"supplier": "EcoFabrics", "price": 15.0},
        "Bamboo Silk": {"supplier": "SilkySustain", "price": 22.0},
        "Organic Linen": {"supplier": "NatureSpun", "price": 13.5}
    }
    
    if os.path.exists(csv_path):
        state["file_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if not rows:
                    state["error_msg"] = "CSV is empty."
                else:
                    header = [h.strip().lower() for h in rows[0]]
                    if header == ["fabric_name", "supplier_name", "price_per_yard"]:
                        state["has_header"] = True
                        
                    correct_count = 0
                    for row in rows[1:]: # Skip header
                        if len(row) == 3:
                            fname = row[0].strip()
                            sname = row[1].strip()
                            try:
                                price = float(row[2].strip())
                            except ValueError:
                                continue
                                
                            state["items_found"].append({"fabric": fname, "supplier": sname, "price": price})
                            
                            if fname in expected_data:
                                if expected_data[fname]["supplier"] == sname and expected_data[fname]["price"] == price:
                                    correct_count += 1
                                    
                    if correct_count == 3 and len(rows) == 4: # 1 header + 3 rows
                        state["is_correct"] = True
                    else:
                        state["error_msg"] = f"Found {correct_count}/3 correct items. Total rows: {len(rows)}."
        except Exception as e:
            state["error_msg"] = str(e)
            
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
