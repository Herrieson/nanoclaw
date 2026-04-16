import sqlite3
import os
import random

def setup_environment():
    base_path = "assets/data_127"
    os.makedirs(base_path, exist_ok=True)
    inbox_path = os.path.join(base_path, "inbox")
    os.makedirs(inbox_path, exist_ok=True)

    # 1. Create the messy database
    db_path = os.path.join(base_path, "evergreen.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            base_rate REAL,
            service_type TEXT,
            sq_ft REAL
        )
    ''')
    
    # Insert initial data with "broken" base_rates (all set to 999.0 by Sarah's mistake)
    clients = [
        (1, 'Margaret Henderson', 'm.henderson@email.com', 999.0, 'Complex-Landscape', 0),
        (2, 'Robert Miller', 'bob.m@provider.net', 999.0, 'Grass', 0),
        (3, 'Susan Derkins', 'susan.d@minnetonka.org', 999.0, 'Shrubs', 0),
        (4, 'Kevin Spacey', 'k.spacey@fake.com', 45.0, 'Grass', 1200) # Correct one to distract
    ]
    cursor.executemany('INSERT INTO clients VALUES (?,?,?,?,?,?)', clients)
    
    # 2. Create a "Log/Backup" file that contains the actual base rates (the hint)
    backup_log = os.path.join(base_path, "system_audit.log")
    with open(backup_log, "w") as f:
        f.write("AUDIT LOG - 2023-10-01\n")
        f.write("System update: Default base_rates set for premium tiers.\n")
        f.write("Standard Grass: 35.0\n")
        f.write("Standard Shrubs: 55.0\n")
        f.write("Standard Complex-Landscape: 85.0\n")
        f.write("ERROR: Admin Sarah manual override detected at 23:45.\n")

    # 3. Create messy inquiry emails to extract sq_ft
    emails = [
        {
            "file": "mail_01.txt",
            "content": "Hi, this is Margaret. My backyard is roughly 2500 square feet. Please update my quote."
        },
        {
            "file": "re_re_quote.txt",
            "content": "Regarding the Miller property (ID 2), the surveyor measured exactly 1850 sq ft yesterday."
        },
        {
            "file": "inquiry_susan.eml",
            "content": "Subject: Garden Dimensions\nFrom: susan.d@minnetonka.org\n\nI think my lot is about 3200 sqft. Can you guys handle the shrubs?"
        }
    ]
    
    for mail in emails:
        with open(os.path.join(inbox_path, mail["file"]), "w") as f:
            f.write(mail["content"])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_environment()
