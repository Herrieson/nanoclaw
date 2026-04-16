import os
import sqlite3
import json

def build_env():
    base_dir = "assets/data_431"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create SQLite DB
    db_path = os.path.join(base_dir, "collection.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            year_made INTEGER,
            price REAL
        )
    """)
    
    # Insert some initial data
    initial_items = [
        ("Brass Hair Clipper", 1940, 45.50),
        ("Art Deco Hair Dryer", 1935, 120.00),
        ("Victorian Hair Pins", 1890, 85.00),
        ("Bakelite Comb Set", 1955, 200.00)
    ]
    c.executemany("INSERT INTO tools (item_name, year_made, price) VALUES (?, ?, ?)", initial_items)
    conn.commit()
    conn.close()
    
    # 2. Create messy folders and files
    collection_dir = os.path.join(base_dir, "vintage_collection")
    os.makedirs(os.path.join(collection_dir, "batch_1"), exist_ok=True)
    os.makedirs(os.path.join(collection_dir, "misc_notes"), exist_ok=True)
    os.makedirs(os.path.join(collection_dir, "estate_sales", "lot_42"), exist_ok=True)
    os.makedirs(os.path.join(collection_dir, "estate_sales", "lot_88"), exist_ok=True)
    
    # Garbage file 1
    with open(os.path.join(collection_dir, "batch_1", "old_inventory.csv"), "w") as f:
        f.write("item,cost\nComb,10\nBrush,15\n")
        
    # Garbage file 2
    with open(os.path.join(collection_dir, "misc_notes", "ideas.txt"), "w") as f:
        f.write("Need to buy more display cabinets for the salon.\nMaybe try a new yoga routine next week.")
        
    # Garbage file 3
    with open(os.path.join(collection_dir, "estate_sales", "lot_88", "auction_summary.json"), "w") as f:
        json.dump({"auction_id": "88", "items": [{"name": "Generic Scissors", "year": 1980, "price_paid": "$12.00"}]}, f)

    # Target file with the needed information
    target_data = {
        "transaction_id": "TXN-99281",
        "date": "2023-10-12",
        "purchased_items": [
            {
                "description": "Silver Marcel Curling Iron",
                "condition": "Good",
                "manufacturing_year": 1922,
                "financials": {
                    "hammer_price": "$125.00",
                    "buyer_premium": "$25.00",
                    "total_price_paid": 150.00
                }
            }
        ]
    }
    with open(os.path.join(collection_dir, "estate_sales", "lot_42", "receipt_final.json"), "w") as f:
        json.dump(target_data, f, indent=4)
        
    # 3. Create the broken python script
    broken_script = """import sqlite3
import os

def calculate_total():
    # Connect to the database
    conn = sqlite3.connect('collection.db')
    c = conn.cursor()
    
    # Fetch all prices
    # Wait, I think my aunt named the table 'tool' or something?
    c.execute("SELECT price FROM tool")
    
    records = c.fetchall()
    total_value = 0
    for row in records:
        total_value += row[0]
        
    print(f"The total value of the collection is: ${total_value}")
    return total_value

if __name__ == "__main__":
    calculate_total()
"""
    with open(os.path.join(base_dir, "calc_value.py"), "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    build_env()
