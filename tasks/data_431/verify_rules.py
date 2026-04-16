import os
import json
import sqlite3
import re

def verify():
    base_dir = "."
    db_path = os.path.join(base_dir, "collection.db")
    total_txt_path = os.path.join(base_dir, "total_value.txt")
    
    state = {
        "db_updated_correctly": False,
        "total_value_correct": False,
        "extracted_total": None
    }
    
    # 1. Check DB
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT item_name, year_made, price FROM tools WHERE item_name LIKE '%Silver Marcel Curling Iron%'")
            row = c.fetchone()
            if row:
                name, year, price = row
                if year == 1922 and abs(float(price) - 150.0) < 0.01:
                    state["db_updated_correctly"] = True
            conn.close()
        except Exception as e:
            pass
            
    # 2. Check total_value.txt
    if os.path.exists(total_txt_path):
        try:
            with open(total_txt_path, "r") as f:
                content = f.read()
                # Initial sum = 450.5. New item = 150. Total expected = 600.5
                numbers = re.findall(r'\d+\.\d+|\d+', content)
                for num in numbers:
                    if abs(float(num) - 600.5) < 0.01:
                        state["total_value_correct"] = True
                        state["extracted_total"] = float(num)
                        break
        except Exception as e:
            pass

    result_path = os.path.join(base_dir, "verify_result.json")
    with open(result_path, "w") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
