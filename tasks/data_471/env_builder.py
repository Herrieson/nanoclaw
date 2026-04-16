import os
import sqlite3
import random
from datetime import datetime, timedelta

def build_env():
    base_dir = "assets/data_471"
    os.makedirs(base_dir, exist_ok=True)
    pos_dir = os.path.join(base_dir, "pos_data")
    os.makedirs(pos_dir, exist_ok=True)

    # 1. Create SQLite Database
    db_path = os.path.join(base_dir, "catalog.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE products (
            code TEXT PRIMARY KEY,
            name TEXT,
            supplier_email TEXT,
            price REAL
        )
    ''')

    catalog = [
        ("ITM-001", "Premium Saffron Threads", "spices@gourmet-imports.com", 120.00),
        ("ITM-002", "Artisan Manchego Cheese", "dairy@spain-foods.es", 45.50),
        ("ITM-003", "Jamón Ibérico de Bellota", "meats@spain-foods.es", 250.00),
        ("ITM-004", "White Truffle Oil", "oils@tuscany-estates.it", 85.00),
        ("ITM-005", "Organic Bomba Rice", "grains@paella-supplies.com", 15.00),
        ("ITM-006", "Smoked Paprika (Pimentón)", "spices@gourmet-imports.com", 12.00),
        ("ITM-007", "Caviar Oscietra", "luxury@seafood-delight.com", 300.00),
        ("ITM-008", "Marcona Almonds", "snacks@spain-foods.es", 22.00)
    ]
    
    cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', catalog)
    conn.commit()
    conn.close()

    # 2. Generate messy log files
    actions = ["RESTOCKED", "PURCHASE", "REFUND", "INVENTORY_CHECK"]
    sold_out_targets = ["ITM-001", "ITM-003", "ITM-005", "ITM-006"] # The ones the agent needs to find

    for i in range(1, 6):
        log_path = os.path.join(pos_dir, f"register_{i}_20231025.log")
        with open(log_path, "w", encoding="utf-8") as f:
            for _ in range(50):
                action = random.choice(actions)
                item = random.choice(catalog)[0]
                qty = random.randint(1, 10)
                timestamp = (datetime.now() - timedelta(minutes=random.randint(1, 1000))).strftime("%Y-%m-%d %H:%M:%S")
                
                # Messy formatting
                f.write(f"[{timestamp}] || ACT: {action} || ITEM_CODE: {item} || QTY_CHANGE: {qty}\n")
                
                # Inject SOLD_OUT events randomly, ensuring targets are hit and duplicated
                if random.random() < 0.15:
                    target = random.choice(sold_out_targets)
                    f.write(f"[{timestamp}] || ACT: SOLD_OUT || ITEM_CODE: {target} || QTY_CHANGE: 0\n")
                    
                    # Add some garbage lines to test parsing
                    f.write(f"ERROR: Cash drawer open too long!\n")
                    f.write(f"[{timestamp}] || ACT: SYSTEM_PING || ITEM_CODE: NONE || QTY_CHANGE: 0\n")

if __name__ == "__main__":
    build_env()
