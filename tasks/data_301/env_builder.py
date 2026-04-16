import os
import json
import sqlite3

def build_env():
    base_dir = "assets/data_301"
    os.makedirs(base_dir, exist_ok=True)
    
    # Create messy JSON log
    donations = [
        {"id": "A1", "desc": "  1940s French Military Trench Coat", "condition": "Good"},
        {"id": "A2", "desc": "Soviet Winter Coat", "condition": "Fair"},
        {"id": "A3", "desc": "FRENCH military Wool Trousers  ", "condition": "Mint"},
        {"id": "A4", "desc": "  french military BERET", "condition": "Good"},
        {"id": "A5", "desc": "US Navy Peacoat", "condition": "Excellent"}
    ]
    
    with open(os.path.join(base_dir, "donations_log.json"), "w", encoding="utf-8") as f:
        json.dump(donations, f, indent=2)
        
    # Create SQLite DB
    db_path = os.path.join(base_dir, "vintage_prices.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE catalog (name TEXT, price REAL)")
    
    prices = [
        ("1940s french military trench coat", 150.0),
        ("soviet winter coat", 60.0),
        ("french military wool trousers", 85.0),
        ("french military beret", 40.0),
        ("us navy peacoat", 120.0)
    ]
    cursor.executemany("INSERT INTO catalog VALUES (?, ?)", prices)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
