import sqlite3
import os
import json

def verify():
    results = {
        "script_fixed": False,
        "db_entry_count": 0,
        "db_integrity": False,
        "logic_bug_resolved": False
    }
    
    db_path = "production.db"
    sync_script = "sync_v2.py"
    
    # 1. Check if the script was modified to remove the 'break' and 'continue'
    if os.path.exists(sync_script):
        with open(sync_script, "r") as f:
            content = f.read()
            if "i > 1000" not in content and "i % 2 == 0" not in content:
                results["logic_bug_resolved"] = True

    # 2. Check Database state
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM wing_data")
            count = cursor.fetchone()[0]
            results["db_entry_count"] = count
            if count == 1024:
                results["db_integrity"] = True
            conn.close()
        except Exception:
            pass

    # Overall pass
    results["script_fixed"] = results["logic_bug_resolved"] and results["db_integrity"]

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
