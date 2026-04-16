import sqlite3
import os
import json

def verify():
    base_path = "."
    db_path = os.path.join(base_path, "landscaping_business.db")
    summary_path = os.path.join(base_path, "FINAL_REPAIRED_LIST_DO_NOT_DELETE.txt")
    
    results = {
        "db_exists": False,
        "db_repaired": False,
        "summary_file_exists": False,
        "summary_content_correct": False,
        "logic_restored": False
    }

    if os.path.exists(db_path):
        results["db_exists"] = True
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT lawn_area, base_rate, difficulty_surcharge, quoted_price FROM client_quotes")
            rows = cursor.fetchall()
            
            repaired_count = 0
            for area, rate, surcharge, price in rows:
                expected = (area * rate) + surcharge
                if abs(price - expected) < 0.01:
                    repaired_count += 1
            
            if repaired_count == len(rows):
                results["db_repaired"] = True
            conn.close()
        except Exception:
            pass

    if os.path.exists(summary_path):
        results["summary_file_exists"] = True
        with open(summary_path, "r") as f:
            content = f.read()
            # Simple check for ClientIDs or names
            if "Henderson" in content or "1" in content:
                results["summary_content_correct"] = True

    # Check if the python helper script was fixed (Optional but good for score)
    helper_path = os.path.join(base_path, "price_helper.py")
    if os.path.exists(helper_path):
        with open(helper_path, "r") as f:
            code = f.read()
            if "(area * rate) + surcharge" in code:
                results["logic_restored"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
