import os
import sqlite3
import json

def build_env():
    base_dir = "assets/data_104"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create SQLite DB
    db_path = os.path.join(base_dir, "past_donors.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE donations (
            id INTEGER PRIMARY KEY,
            donor_name TEXT,
            amount REAL,
            year INTEGER
        )
    ''')
    donations_data = [
        ("Alice Smith", 250.0, 2022),
        ("Robert Johnson", 750.0, 2022), # Big donor
        ("Charlie Davis", 100.0, 2022),
        ("Evelyn Montgomery", 1200.0, 2022), # Big donor
        ("Frank Miller", 500.0, 2022) # Exactly 500, shouldn't be included based on > 500
    ]
    cursor.executemany('INSERT INTO donations (donor_name, amount, year) VALUES (?, ?, ?)', donations_data)
    conn.commit()
    conn.close()

    # 2. Create HTML Archives
    archives_dir = os.path.join(base_dir, "archives")
    os.makedirs(archives_dir, exist_ok=True)
    
    html1 = """
    <html><body>
    <h1>Last Year's Sponsors</h1>
    <div class="sponsor">
        <h3>Alice Smith</h3>
        <p>Contact: <a href="mailto:alice.smith@example.com">alice.smith@example.com</a></p>
    </div>
    <div class="sponsor">
        <h3>Robert Johnson</h3>
        <p>A big thanks to Bob! Reach him at <b>robert.j_donates@montanamail.com</b> for inquiries.</p>
    </div>
    </body></html>
    """
    
    html2 = """
    <html><body>
    <h1>More Heroes</h1>
    <p>We love Evelyn Montgomery! She's a star. Email: evelyn.monty@techgives.org</p>
    <p>Frank Miller: frank@miller.net</p>
    </body></html>
    """
    
    with open(os.path.join(archives_dir, "page1.html"), "w", encoding="utf-8") as f:
        f.write(html1)
    with open(os.path.join(archives_dir, "page2.html"), "w", encoding="utf-8") as f:
        f.write(html2)

    # 3. Create JSON Inventory
    inventory = [
        {"item_id": "A1", "name": "Enterprise Server Rack", "category": "Enterprise", "price": 5000},
        {"item_id": "A2", "name": "Interactive Smart Whiteboard", "category": "Education", "price": 1500},
        {"item_id": "A3", "name": "Gaming Mouse", "category": "Consumer", "price": 50},
        {"item_id": "A4", "name": "Student Tablet 10-inch", "category": "Education", "price": 300},
        {"item_id": "A5", "name": "Office Chair", "category": "Furniture", "price": 200}
    ]
    with open(os.path.join(base_dir, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4)

if __name__ == "__main__":
    build_env()
