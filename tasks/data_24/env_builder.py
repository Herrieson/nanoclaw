import os
import sqlite3
import random
from datetime import datetime

def setup_environment():
    base_path = "assets/data_24"
    os.makedirs(base_path, exist_ok=True)

    # 1. Create a corrupted SQLite database
    db_path = os.path.join(base_path, "orders.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        weight_kg REAL,
        total_price REAL,
        status TEXT,
        delivery_date TEXT
    )''')

    # Data: Some correct, some null, some wrong
    orders = [
        (101, 'Boise Fresh Market', 1200.0, 5400.0, 'PAID', '2024-05-20'),
        (102, 'Mountain View Groceries', 2500.0, None, 'PENDING', '2024-05-20'),
        (103, 'Spuds & More', 1800.0, 3200.0, 'ERROR', '2024-05-20'),
        (104, 'Valley Wholesale', 900.0, None, 'PAID', '2024-05-20'),
        (105, 'Idaho Falls Organics', 3100.0, 8900.0, 'PENDING', '2024-05-20')
    ]
    cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', orders)
    conn.commit()
    conn.close()

    # 2. Create Delivery Logs (The "Source of Truth")
    log_content = [
        "2024-05-19 08:00:01 INFO: System update initiated by user 'j_miller_99'.",
        "2024-05-19 08:15:22 DATA: Order 102 total_price set to 4250.00 via API.",
        "2024-05-19 08:15:45 DATA: Order 104 total_price set to 1150.00 via API.",
        "2024-05-19 08:20:10 WARNING: Database write conflict on Order 103.",
        "2024-05-19 08:21:00 ERROR: Script 'sync_inventory.py' crashed. Traceback: ..."
    ]
    with open(os.path.join(base_path, "system.log"), "w") as f:
        f.write("\n".join(log_content))

    # 3. Create the broken script
    broken_script = """
import sqlite3
# This script was supposed to sync prices but it clears them instead.
def sync():
    conn = sqlite3.connect('orders.db')
    # cursor.execute("UPDATE orders SET total_price = NULL WHERE status = 'PENDING'")
    # Whoops... 
    conn.close()
"""
    with open(os.path.join(base_path, "sync_inventory.py"), "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    setup_environment()
