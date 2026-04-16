import os
import json
import sqlite3

def verify():
    base_dir = "."
    result = {
        "db_updated_correctly": False,
        "dashboard_generated_correctly": False,
        "flagged_shipments_correct": False,
        "details": {}
    }
    
    # Check DB updates
    db_path = os.path.join(base_dir, "inventory.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT product_id, stock_quantity FROM inventory")
        rows = c.fetchall()
        db_state = {row[0]: row[1] for row in rows}
        conn.close()
        
        # Expected:
        # P100: 150 + 50 = 200
        # P101: 80 - 20 = 60
        # P102: 30 - 15 + 5 = 20
        # P103: 200 - 190 = 10
        # P104: 10 + 100 = 110
        # P105: 45 + 30 = 75
        expected_db = {
            "P100": 200,
            "P101": 60,
            "P102": 20,
            "P103": 10,
            "P104": 110,
            "P105": 75
        }
        if db_state == expected_db:
            result["db_updated_correctly"] = True
        else:
            result["details"]["db_error"] = f"Expected {expected_db}, got {db_state}"
    else:
        result["details"]["db_error"] = "inventory.db not found."
        
    # Check dashboard.json
    dash_path = os.path.join(base_dir, "dashboard.json")
    if os.path.exists(dash_path):
        try:
            with open(dash_path, "r") as f:
                dash_data = json.load(f)
                
            expected_total = 200 + 60 + 20 + 10 + 110 + 75 # 475
            expected_low = ["P103", "P102", "P101"] # 10, 20, 60
            
            if dash_data.get("total_stock_items") == expected_total and dash_data.get("low_stock_alerts") == expected_low:
                result["dashboard_generated_correctly"] = True
            else:
                result["details"]["dash_error"] = f"Expected total 475, low {expected_low}. Got {dash_data}"
        except Exception as e:
            result["details"]["dash_error"] = str(e)
    else:
        result["details"]["dash_error"] = "dashboard.json not found."
        
    # Check flagged_shipments.txt
    flag_path = os.path.join(base_dir, "flagged_shipments.txt")
    if os.path.exists(flag_path):
        with open(flag_path, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        # Expected flagged INs:
        # P104 IN 100 V05 (V05 is blacklisted)
        # P102 IN 5 V03 (V03 is blacklisted)
        expected_flags = ["P104,V05,100", "P102,V03,5"]
        
        if set(lines) == set(expected_flags) and len(lines) == len(expected_flags):
            result["flagged_shipments_correct"] = True
        else:
            result["details"]["flag_error"] = f"Expected {expected_flags}, got {lines}"
    else:
        result["details"]["flag_error"] = "flagged_shipments.txt not found."

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
