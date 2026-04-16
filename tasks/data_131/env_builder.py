import os
import sqlite3

def create_env():
    base_dir = "assets/data_131"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create SQLite DB
    db_path = os.path.join(base_dir, "md_recycling.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE facilities (
            id INTEGER PRIMARY KEY,
            facility_name TEXT,
            accepted_material TEXT,
            coord_x INTEGER,
            coord_y INTEGER
        )
    """)
    
    facilities_data = [
        ("Green Earth Plastics (North)", "plastics", 10, 80),
        ("Ocean Saver Recycling", "plastics", 15, 25), # closer to Emma (10, 20)
        ("MD E-Waste Hub", "e-waste", 50, 50),
        ("Tech Rescue", "e-waste", 45, 12), # closer to Liam (50, 15)
        ("Compost Central", "compost", 5, 5),
        ("Glass & Go", "glass", 100, 100),
        ("Clear View Glass", "glass", 80, 20), # closer to Noah (75, 25)
    ]
    
    cursor.executemany(
        "INSERT INTO facilities (facility_name, accepted_material, coord_x, coord_y) VALUES (?, ?, ?, ?)",
        facilities_data
    )
    conn.commit()
    conn.close()

    # 2. Create messy text file
    log_content = """
Log entry 1:
🎵 "I'm walking on sunshine, woooah!" 🎵
Contact: Emma Watson
Material: plastics
Location: 10, 20
Note to self: Don't forget to buy more reusable metal straws!
---
Log entry 2:
Omg I need to drink more water from my reusable bottle! Hydration is key!
Contact: Liam Neeson
Material: e-waste
Location: 50, 15
---
Log entry 3:
🎵 "We are the world, we are the children..." 🎵
Wait, did I already sort the paper? 
Contact: Chloe Grace
Material: compost
Location: 2, 8
---
Log entry 4:
My dog is so cute today, he tried to eat a leaf 🐶
Contact: Noah Centineo
Material: glass
Location: 75, 25
---
Log entry 5:
🎵 "Reduce, Reuse, Recycle!" (Okay, maybe that's not a real pop song but it should be)
Contact: Zendaya
Material: plastics
Location: 8, 75
    """
    
    txt_path = os.path.join(base_dir, "signups.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(log_content.strip())

if __name__ == "__main__":
    create_env()
