import sqlite3
import os
import json

def verify():
    results = {
        "db_updated": False,
        "correct_amount": False,
        "final_bonus_value": 0,
        "script_fixed": False
    }
    
    db_path = "payroll_pending.db"
    script_path = "reconcile_bonus.py"
    
    # Check if DB exists
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT bonus_amount FROM pending_payments WHERE employee_id = 101")
            row = cursor.fetchone()
            if row:
                # Base 1500 + (4 sessions * 75) = 1500 + 300 = 1800
                results["final_bonus_value"] = row[0]
                if row[0] == 1800.0:
                    results["db_updated"] = True
                    results["correct_amount"] = True
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")

    # Check if script was modified
    if os.path.exists(script_path):
        with open(script_path, "r") as f:
            content = f.read()
            if "UPDATE pending_payments" in content.upper() and "pass" not in content:
                results["script_fixed"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
