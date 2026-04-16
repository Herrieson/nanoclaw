import os
import sqlite3
import json

def verify():
    result = {
        "db_exists": False,
        "table_exists": False,
        "total_rows": 0,
        "date_format_correct": False,
        "total_value_correct": False,
        "volume_file_exists": False,
        "volume_correct": False
    }
    
    db_path = "trades.db"
    vol_path = "brka_volume.txt"
    
    if os.path.exists(db_path):
        result["db_exists"] = True
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
            if cursor.fetchone():
                result["table_exists"] = True
                
                # Check rows
                cursor.execute("SELECT COUNT(*) FROM transactions")
                result["total_rows"] = cursor.fetchone()[0]
                
                # Check dates
                cursor.execute("SELECT date FROM transactions")
                dates = [r[0] for r in cursor.fetchall()]
                # All dates should match YYYY-MM-DD
                import re
                if all(re.match(r"^\d{4}-\d{2}-\d{2}$", str(d).strip()) for d in dates) and len(dates) == 9:
                    result["date_format_correct"] = True
                    
                # Check total_value calculation for a specific row
                cursor.execute("SELECT quantity, price, total_value FROM transactions WHERE ticker LIKE '%AAPL%' LIMIT 1")
                row = cursor.fetchone()
                if row and abs(float(row[0]) * float(row[1]) - float(row[2])) < 0.01:
                    result["total_value_correct"] = True
                    
        except Exception as e:
            result["db_error"] = str(e)
        finally:
            if 'conn' in locals():
                conn.close()
                
    if os.path.exists(vol_path):
        result["volume_file_exists"] = True
        try:
            with open(vol_path, "r") as f:
                content = f.read().strip()
                # BRK.A total volume: 2 + 1 + 3 = 6
                if content == "6" or content == "6.0":
                    result["volume_correct"] = True
        except:
            pass
            
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
