import os
import json
import sqlite3

def verify():
    workspace_dir = "."
    db_path = os.path.join(workspace_dir, "inventory.db")
    birds_file = os.path.join(workspace_dir, "birds_seen.txt")
    
    state = {
        "db_exists": False,
        "birds_file_exists": False,
        "db_values": {},
        "birds_found": []
    }
    
    if os.path.exists(db_path):
        state["db_exists"] = True
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, quantity FROM products")
            rows = cursor.fetchall()
            for name, qty in rows:
                state["db_values"][name] = qty
            conn.close()
        except Exception as e:
            state["db_error"] = str(e)
            
    if os.path.exists(birds_file):
        state["birds_file_exists"] = True
        try:
            with open(birds_file, "r", encoding="utf-8") as f:
                content = f.read().lower()
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                state["birds_found"] = lines
        except Exception as e:
            state["birds_file_error"] = str(e)
            
    with open(os.path.join(workspace_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
