import os
import sqlite3
import json

def build_env():
    base_dir = "assets/data_245"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create EPA emissions JSON
    epa_data = {
        "diesel generator": 15.0,
        "heavy excavator": 25.5,
        "electric forklift": 1.2,
        "industrial crane": 18.0,
        "gasoline pump": 8.5
    }
    with open(os.path.join(base_dir, "epa_emissions.json"), "w") as f:
        json.dump(epa_data, f, indent=4)

    # 2. Create Portfolio SQLite Database
    db_path = os.path.join(base_dir, "portfolio.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE leases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            duration_months INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    # Insert data
    # Some expired, some active, messy casing
    leases_data = [
        ('DIESEL GENERATOR', 2, 12, 'active'),       # 2 * 12 * 15.0 = 360.0
        ('Heavy Excavator', 1, 24, 'active'),        # 1 * 24 * 25.5 = 612.0
        ('Electric Forklift', 5, 36, 'active'),      # 5 * 36 * 1.2 = 216.0
        ('gasoline pump', 10, 6, 'active'),          # 10 * 6 * 8.5 = 510.0
        ('Industrial Crane', 1, 12, 'expired'),      # Ignore
        ('Diesel Generator', 1, 6, 'active'),        # 1 * 6 * 15.0 = 90.0  -> Total Diesel: 450.0
        ('HEAVY excavator', 2, 6, 'active'),         # 2 * 6 * 25.5 = 306.0 -> Total Heavy: 918.0
        ('ELECTRIC forklift', 2, 12, 'expired'),     # Ignore
    ]

    cursor.executemany('''
        INSERT INTO leases (equipment_type, quantity, duration_months, status)
        VALUES (?, ?, ?, ?)
    ''', leases_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
