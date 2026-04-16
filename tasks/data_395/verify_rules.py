import os
import sqlite3
import json

def verify():
    base_dir = "."
    db_path = os.path.join(base_dir, "library.db")
    
    state = {
        "db_exists": False,
        "clarke_found": False,
        "prince_found": False,
        "sagan_found": False,
        "extra_books_inserted": 0
    }
    
    if os.path.exists(db_path):
        state["db_exists"] = True
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT isbn, title, author FROM books")
            rows = cursor.fetchall()
            
            target_isbns = {
                "978-0451457998": "clarke_found",
                "978-0156012195": "prince_found",
                "978-0345331359": "sagan_found"
            }
            
            valid_count = 0
            for row in rows:
                isbn = row[0]
                if isbn in target_isbns:
                    state[target_isbns[isbn]] = True
                    valid_count += 1
                else:
                    state["extra_books_inserted"] += 1
                    
            conn.close()
        except Exception as e:
            state["error"] = str(e)
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
