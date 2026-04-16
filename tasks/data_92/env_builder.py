import os
import sqlite3
import random

def setup_environment():
    base_path = "assets/data_92"
    os.makedirs(base_path, exist_ok=True)

    # 1. Create a corrupted database
    db_path = os.path.join(base_path, "landscaping_business.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE client_quotes (
        id INTEGER PRIMARY KEY,
        client_name TEXT,
        lawn_area REAL,
        base_rate REAL,
        difficulty_surcharge REAL,
        quoted_price REAL
    )''')

    # Data: Correct logic should be (area * rate) + surcharge
    # We will inject "corrupted" prices (Area * Rate * 100 + random noise)
    clients = [
        ("Henderson", 500, 0.5, 50),
        ("Miller", 1200, 0.45, 100),
        ("Snyder", 300, 0.6, 20),
        ("Davis", 800, 0.5, 75),
        ("Wilson", 1500, 0.4, 200)
    ]

    for name, area, rate, surcharge in clients:
        # The corrupted price: area * rate * 100
        corrupted_price = (area * rate * 100) + random.randint(1, 50)
        cursor.execute('''INSERT INTO client_quotes 
            (client_name, lawn_area, base_rate, difficulty_surcharge, quoted_price) 
            VALUES (?, ?, ?, ?, ?)''', (name, area, rate, surcharge, corrupted_price))
    
    conn.commit()
    conn.close()

    # 2. Create a "broken" helper script that has the wrong logic
    script_path = os.path.join(base_path, "price_helper.py")
    with open(script_path, "w") as f:
        f.write('''
def calculate_quote(area, rate, surcharge):
    # I think I changed this by mistake? 
    # Return (area * rate * 100) + 10 # This is wrong!
    return (area * rate * 100) + 10
''')

    # 3. Create a log file that contains the "clue" to the original logic
    log_path = os.path.join(base_path, "system_audit.log")
    with open(log_path, "w") as f:
        f.write("[2023-10-23 08:15:22] INFO: Backup initiated.\n")
        f.write("[2023-10-23 09:00:01] WARNING: User changed price_helper.py\n")
        f.write("[2023-10-23 09:05:44] TRACE: Previous logic was: (area * rate) + surcharge\n")
        f.write("[2023-10-23 09:10:12] ERROR: Bulk update applied to client_quotes table using wrong formula.\n")

if __name__ == "__main__":
    setup_environment()
