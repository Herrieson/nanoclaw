import os
import sqlite3

def build_env():
    base_dir = "assets/data_421"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the unstructured orders text file
    orders_content = """Hey Boss,

Here are the notes for this week's repair jobs:
- George brought in his old push mower, needs a new blade. The part ID is MOW-001.
- Fatima's stand mixer burnt out its motor. We need BLN-202 to fix it.
- We're also out of generic bearings, so please order BRG-050.
- And I noticed we need a new rubber seal for the pressure washers, part ID SEL-007.

Thanks,
Mike
"""
    with open(os.path.join(base_dir, "orders.txt"), "w", encoding="utf-8") as f:
        f.write(orders_content)

    # 2. Create the SQLite catalog database
    db_path = os.path.join(base_dir, "catalog.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id TEXT,
            supplier_code TEXT,
            price REAL,
            is_eco_friendly INTEGER
        )
    ''')

    # Insert data
    # Logic:
    # MOW-001: Eco-friendly available, pick the eco one despite higher price.
    # BLN-202: No eco-friendly, pick the cheapest.
    # BRG-050: Multiple eco-friendly, pick the cheapest among eco-friendly.
    # SEL-007: No eco-friendly, pick the cheapest.
    # XYZ-999: Noise data.
    
    parts_data = [
        ("MOW-001", "SUP-A1", 25.00, 0),
        ("MOW-001", "SUP-A2", 28.00, 1), # <-- Target for MOW-001
        ("BLN-202", "SUP-B1", 45.00, 0),
        ("BLN-202", "SUP-B2", 40.00, 0), # <-- Target for BLN-202
        ("BLN-202", "SUP-B3", 42.00, 0),
        ("BRG-050", "SUP-C1", 5.00, 1),  # <-- Target for BRG-050
        ("BRG-050", "SUP-C2", 6.00, 1),
        ("BRG-050", "SUP-C3", 4.00, 0),  # Not eco-friendly, shouldn't be picked
        ("SEL-007", "SUP-D1", 2.50, 0),  # <-- Target for SEL-007
        ("SEL-007", "SUP-D2", 3.00, 0),
        ("XYZ-999", "SUP-X1", 10.00, 1)  # Not in orders
    ]

    cursor.executemany('''
        INSERT INTO parts (part_id, supplier_code, price, is_eco_friendly)
        VALUES (?, ?, ?, ?)
    ''', parts_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
