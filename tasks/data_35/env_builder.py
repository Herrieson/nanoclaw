import os
import sqlite3

def build_env():
    base_dir = "assets/data_35"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the inventory log
    log_content = """Date: 2023-10-01 | Item: Organic Cotton | Notes: Stored in bin A | STATUS: OK
Date: 2023-10-05 | Item: Hemp Canvas | Notes: Need for new tote bags | STATUS: LOW STOCK
Date: 2023-10-10 | Item: Recycled Polyester Thread | Notes: Black and White | STATUS: OK
Date: 2023-10-15 | Item: Bamboo Silk | Notes: Planning a summer blouse | STATUS: LOW STOCK
Date: 2023-10-20 | Item: Organic Linen | Notes: Good for breathable pants | STATUS: LOW STOCK
Date: 2023-10-22 | Item: Wool Yarn | Notes: Winter prep | STATUS: OK
"""
    with open(os.path.join(base_dir, "inventory.log"), "w", encoding="utf-8") as f:
        f.write(log_content)

    # 2. Create the SQLite database
    db_path = os.path.join(base_dir, "supplier_db.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fabric_name TEXT,
            supplier_name TEXT,
            price_per_yard REAL,
            eco_score INTEGER
        )
    ''')
    
    # Insert mock data
    # We need: Hemp Canvas, Bamboo Silk, Organic Linen
    
    data = [
        # Hemp Canvas
        ("Hemp Canvas", "CheapThreads", 10.00, 5), # Cheap but low eco
        ("Hemp Canvas", "EcoFabrics", 15.00, 9),   # <--- Target
        ("Hemp Canvas", "GreenWeave", 16.00, 10),  # Good eco, not cheapest
        ("Hemp Canvas", "NatureBound", 15.50, 8),  # Meets eco, not cheapest
        
        # Bamboo Silk
        ("Bamboo Silk", "SilkySustain", 22.00, 8), # <--- Target
        ("Bamboo Silk", "LuxEco", 25.00, 9),
        ("Bamboo Silk", "FastFibers", 12.00, 3),
        
        # Organic Linen
        ("Organic Linen", "LinensRUs", 12.00, 7),  # Fails eco score
        ("Organic Linen", "NatureSpun", 13.50, 9), # <--- Target
        ("Organic Linen", "PureLinen", 14.00, 8),
        
        # Irrelevant items
        ("Organic Cotton", "CottonCo", 8.00, 9),
        ("Wool Yarn", "Sheepish", 5.00, 10)
    ]
    
    cursor.executemany('''
        INSERT INTO catalog (fabric_name, supplier_name, price_per_yard, eco_score)
        VALUES (?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
