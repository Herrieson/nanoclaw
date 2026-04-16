import os
import sqlite3

def build_env():
    base_dir = "assets/data_199"
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "inventory.db")
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    initial_inventory = [
        ('Local Honey', 20, 8.50),
        ('Organic Carrots', 15, 2.99),
        ('Milk', 10, 3.50),
        ('Sourdough Bread', 5, 5.00),
        ('Eggs', 12, 4.00)
    ]
    
    cursor.executemany('INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)', initial_inventory)
    conn.commit()
    conn.close()
    
    notes_content = """Monday morning: The kids left a huge mess in the kitchen. Sold 5 jars of Local Honey. Heard a Red-tailed Hawk calling from the old oak tree! 
Tuesday: Restocked! bought 10 Organic Carrots from the Johnson farm. Billy forgot to sweep the aisles again. We sold 2 gallons of Milk. Saw a Northern Cardinal near the feeder, beautiful red.
Wednesday: Had to throw away 2 Organic Carrots, they got squished under a crate. Sold 1 loaf of Sourdough Bread.
Thursday: Quiet day. An American Robin was singing all afternoon. 
Friday: Sold another 3 jars of Local Honey. Found a dead rat near the bins, disgusting."""
    
    with open(os.path.join(base_dir, "notes_from_this_week.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)

if __name__ == "__main__":
    build_env()
