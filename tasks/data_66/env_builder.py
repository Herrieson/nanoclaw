import os
import sqlite3
import random

def setup_environment():
    base_path = "assets/data_66/inventory_system"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)

    # 1. Create fragmented SQLite Database
    db_path = os.path.join(base_path, "pos_backup.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE sales (isbn TEXT, title TEXT, category TEXT, quantity INTEGER, date TEXT)''')
    
    eco_books = [
        ("978-01", "The Silent Spring Revisit", "Eco", 12),
        ("978-02", "Sustainable Living 101", "Eco", 8),
        ("978-03", "Solar Power Dreams", "Eco", 20),
        ("978-04", "Plastic Free World", "Eco", 3)
    ]
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, '2023-10-15')", eco_books)
    conn.commit()
    conn.close()

    # 2. Create raw log files with missing data
    log_content = [
        "2023-11-01 | SALE | ISBN: 978-01 | QTY: 5",
        "2023-11-05 | ERROR | System Timeout",
        "2023-11-10 | SALE | ISBN: 978-03 | QTY: 10",
        "2023-11-12 | SALE | ISBN: 978-05 | TITLE: Ocean Conservation | CAT: Eco | QTY: 18",
        "2023-11-20 | INFO | Inventory check performed"
    ]
    with open(os.path.join(base_path, "logs/daily_sales.log"), "w") as f:
        f.write("\n".join(log_content))

    # 3. Create distracting personal files
    with open(os.path.join(base_path, "meal_prep_monday.csv"), "w") as f:
        f.write("Meal,Calories,Protein\nQuinoa Bowl,450,15g\nSmoothie,300,10g")
    
    with open(os.path.join(base_path, "skate_park_vibe.txt"), "w") as f:
        f.write("Don't forget to practice the kickflip. Meet Sam at 5pm.")

    # 4. A hidden "clutter" file that looks like data but isn't
    with open(os.path.join(base_path, "logs/temp_cache_092.tmp"), "w") as f:
        f.write("978-99 | Junk Data | Category: Fiction | QTY: 100")

if __name__ == "__main__":
    setup_environment()
