import os
import csv
import sqlite3

def build_env():
    asset_dir = "assets/data_310"
    os.makedirs(asset_dir, exist_ok=True)

    # 1. Create batches.txt (Messy log format)
    batches_data = [
        "LOG ENT: B100 | Type: Citrus Blast | Ingredients: Lemon, Lye, Water",
        "LOG ENT: B101 | Type: Organic Lavender Soap | Ingredients: Lye, Water, Lavender Oil", # Faulty
        "LOG ENT: B102 | Type: Organic Lavender Soap | Ingredients: Lye, Water, Lavender Oil, Aloe Vera Extract",
        "LOG ENT: B103 | Type: Rose Petal Wash | Ingredients: Rose water, Lye",
        "LOG ENT: B104 | Type: Organic Lavender Soap | Ingredients: Lavender Oil, Lye, Glycerin", # Faulty
        "LOG ENT: B105 | Type: Organic Lavender Soap | Ingredients: Aloe Vera Extract, Lye, Lavender Oil",
        "LOG ENT: B106 | Type: Minty Fresh Scrub | Ingredients: Mint, Lye, Sand, Water",
        "LOG ENT: B107 | Type: Organic Lavender Soap | Ingredients: Water, Lye, Lavender Oil, Coconut Oil", # Faulty
        "LOG ENT: B108 | Type: Organic Lavender Soap | Ingredients: Lavender Oil, Aloe Vera Extract, Shea Butter, Lye"
    ]
    
    with open(os.path.join(asset_dir, "batches.txt"), "w") as f:
        for line in batches_data:
            f.write(line + "\n")

    # 2. Create shifts.csv
    shifts_data = [
        {"BatchID": "B100", "Date": "2023-10-01", "WorkerID": "W02"},
        {"BatchID": "B101", "Date": "2023-10-01", "WorkerID": "W01"},
        {"BatchID": "B102", "Date": "2023-10-02", "WorkerID": "W03"},
        {"BatchID": "B103", "Date": "2023-10-02", "WorkerID": "W05"},
        {"BatchID": "B104", "Date": "2023-10-03", "WorkerID": "W04"},
        {"BatchID": "B105", "Date": "2023-10-03", "WorkerID": "W01"},
        {"BatchID": "B106", "Date": "2023-10-04", "WorkerID": "W02"},
        {"BatchID": "B107", "Date": "2023-10-04", "WorkerID": "W06"},
        {"BatchID": "B108", "Date": "2023-10-05", "WorkerID": "W03"}
    ]
    
    with open(os.path.join(asset_dir, "shifts.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["BatchID", "Date", "WorkerID"])
        writer.writeheader()
        writer.writerows(shifts_data)

    # 3. Create employees.db
    db_path = os.path.join(asset_dir, "employees.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE workers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT
        )
    """)
    
    workers_data = [
        ("W01", "David Nguyen", "555-0101"),
        ("W02", "Sarah Jenkins", "555-0102"),
        ("W03", "Mike Ross", "555-0103"),
        ("W04", "Emily Chen", "555-0104"),
        ("W05", "Rachel Goldberg", "555-0105"),
        ("W06", "Aaron Levi", "555-0106")
    ]
    
    cursor.executemany("INSERT INTO workers (id, name, phone) VALUES (?, ?, ?)", workers_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
