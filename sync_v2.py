import sqlite3
import os

def sync():
    db_path = "assets/data_208/production.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS wing_data (id INTEGER PRIMARY KEY, status TEXT, val REAL)")
    
    # Faulty logic: It stops at 1000 instead of 1024 due to a hardcoded limit
    # and ignores even-numbered IDs because of a 'continue' bug
    for i in range(1, 1025):
        if i > 1000:
            break
        if i % 2 == 0:
            continue
        cursor.execute("INSERT OR REPLACE INTO wing_data (id, status, val) VALUES (?, ?, ?)", (i, 'active', i * 0.5))
    
    conn.commit()
    conn.close()
    print("Sync completed successfully.")

if __name__ == "__main__":
    sync()