import os
import sqlite3
import json

def verify():
    base_dir = "."
    db_path = os.path.join(base_dir, "my_comics.db")
    meta_path = os.path.join(base_dir, "expected_meta.json")
    
    result = {
        "db_created": False,
        "table_exists": False,
        "columns_correct": False,
        "row_count": 0,
        "expected_row_count": 0,
        "junk_filtered": False,
        "data_accuracy": 0
    }
    
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
            result["expected_row_count"] = meta.get("expected_valid_rows", 80)
            
    if not os.path.exists(db_path):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return
        
    result["db_created"] = True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comics'")
        if not cursor.fetchone():
            conn.close()
            with open("verify_result.json", "w") as f:
                json.dump(result, f)
            return
            
        result["table_exists"] = True
        
        # Check columns
        cursor.execute("PRAGMA table_info(comics)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        if "title" in columns and "issue" in columns and "publisher" in columns:
            result["columns_correct"] = True
            
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM comics")
        row_count = cursor.fetchone()[0]
        result["row_count"] = row_count
        
        if row_count == result["expected_row_count"]:
            result["junk_filtered"] = True
            
        # Check data samples
        cursor.execute("SELECT publisher FROM comics WHERE publisher IS NULL OR publisher = ''")
        null_pubs = cursor.fetchall()
        if len(null_pubs) == 0 and result["junk_filtered"]:
            result["data_accuracy"] = 100
            
        conn.close()
        
    except Exception as e:
        result["error"] = str(e)
        
    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
