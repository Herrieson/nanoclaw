import os
import sqlite3
import random

def build_env():
    # Define the target directory for the environment assets
    asset_dir = "assets/data_453"
    os.makedirs(asset_dir, exist_ok=True)

    # 1. Create SQLite Database
    db_path = os.path.join(asset_dir, "students.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE registrations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            emergency_contact TEXT NOT NULL,
            waiver_signed INTEGER NOT NULL
        )
    ''')

    students = [
        (101, "Alice Smith", "555-0101", 1),
        (102, "Bob Johnson", "555-0102", 0), # No waiver
        (103, "Charlie Davis", "555-0103", 1),
        (104, "Diana Prince", "555-0104", 1),
        (105, "Evan Wright", "555-0105", 1),
        (106, "Fiona Gallagher", "555-0106", 0), # No waiver
        (107, "George Miller", "555-0107", 1),
        (108, "Hannah Abbott", "555-0108", 1),
    ]
    
    cursor.executemany('INSERT INTO registrations VALUES (?, ?, ?, ?)', students)
    conn.commit()
    conn.close()

    # 2. Create the messy log file
    log_path = os.path.join(asset_dir, "portal_dump.log")
    
    log_entries = [
        "2023-10-01 10:15:02 [INFO] Student_ID:101 || dietary_pref:Vegan || status:ACTIVE",
        "2023-10-01 10:16:05 [WARN] SID: 102 - Diet: None - Missing documents",
        "2023-10-01 10:18:22 [INFO] Student_ID:103 || dietary_pref:Gluten-Free || status:ACTIVE",
        "2023-10-01 10:20:00 [DEBUG] system check ok",
        "2023-10-01 10:22:11 [INFO] Student_ID:104 || dietary_pref:None || status:ACTIVE",
        "2023-10-01 10:25:33 [INFO] Student_ID:105 || dietary_pref:Vegetarian || status:ACTIVE",
        "2023-10-01 10:27:01 [WARN] SID: 106 - Diet: None - Pending waiver",
        "2023-10-01 10:30:45 [INFO] Student_ID:107 || dietary_pref:None || status:ACTIVE",
        "2023-10-01 10:35:12 [INFO] Student_ID:108 || dietary_pref:Vegan || status:ACTIVE",
    ]
    
    with open(log_path, "w") as f:
        for entry in log_entries:
            f.write(entry + "\n")

if __name__ == "__main__":
    build_env()
