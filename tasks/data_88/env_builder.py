import os
import sqlite3

def build_env():
    base_dir = "assets/data_88"
    os.makedirs(base_dir, exist_ok=True)
    
    db_path = os.path.join(base_dir, "legacy_csa.db")
    
    # Remove if exists for fresh build
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            join_date TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE contributions (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vol_id INTEGER,
            item_name TEXT,
            category TEXT,
            base_points REAL,
            FOREIGN KEY(vol_id) REFERENCES volunteers(id)
        )
    """)
    
    # Insert volunteers
    volunteers = [
        ("David S.", "2020-03-15"),
        ("Maria G.", "2021-06-22"),
        ("John D.", "2019-11-01"),
        ("Sarah Connor", "2022-01-10")
    ]
    cursor.executemany("INSERT INTO volunteers (name, join_date) VALUES (?, ?)", volunteers)
    
    # Insert contributions
    contributions = [
        # David S. (id=1)
        (1, "Organic Kale", "Leafy Greens", 10.0),      # 10 * 1.5 = 15
        (1, "Carrots", "Root Vegetables", 20.0),        # 20
        (1, "Swiss Chard", "Leafy Greens", 8.0),        # 8 * 1.5 = 12
                                                        # Total = 47.0
        # Maria G. (id=2)
        (2, "Spinach", "Leafy Greens", 20.0),           # 20 * 1.5 = 30
        (2, "Apples", "Fruits", 15.0),                  # 15
        (2, "Beets", "Root Vegetables", 5.0),           # 5
                                                        # Total = 50.0
        # John D. (id=3) - noise data
        (3, "Lettuce", "Leafy Greens", 12.0),
        
        # Sarah Connor (id=4) - noise data
        (4, "Potatoes", "Root Vegetables", 30.0)
    ]
    cursor.executemany("""
        INSERT INTO contributions (vol_id, item_name, category, base_points) 
        VALUES (?, ?, ?, ?)
    """, contributions)
    
    conn.commit()
    conn.close()
    print(f"Environment built successfully at {base_dir}")

if __name__ == "__main__":
    build_env()
