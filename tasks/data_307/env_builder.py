import os
import sqlite3

def build_env():
    base_dir = "assets/data_307"
    os.makedirs(base_dir, exist_ok=True)
    db_path = os.path.join(base_dir, "blueprints.db")

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE models (model_name TEXT)")
    c.execute("CREATE TABLE parts (part_id TEXT, description TEXT)")
    c.execute("CREATE TABLE model_parts (model_name TEXT, part_id TEXT, required_qty INTEGER)")

    models = [("Peterbilt 379",), ("Kenworth W900",), ("Mack R-Model",), ("Volvo VNL",)] 
    c.executemany("INSERT INTO models VALUES (?)", models)

    parts = [
        ("P101", "Wheels"), 
        ("P102", "Axles"), 
        ("P103", "Exhaust"), 
        ("P104", "Cabin"), 
        ("P105", "Grille"), 
        ("P106", "Mudflaps")
    ]
    c.executemany("INSERT INTO parts VALUES (?, ?)", parts)

    reqs = [
        ("Peterbilt 379", "P101", 10),
        ("Peterbilt 379", "P102", 4),
        ("Peterbilt 379", "P103", 2),
        ("Kenworth W900", "P101", 8),
        ("Kenworth W900", "P104", 6),
        ("Kenworth W900", "P105", 1),
        ("Mack R-Model", "P102", 2),
        ("Mack R-Model", "P106", 4),
        ("Volvo VNL", "P101", 10), 
    ]
    c.executemany("INSERT INTO model_parts VALUES (?, ?, ?)", reqs)
    conn.commit()
    conn.close()

    log_dir = os.path.join(base_dir, "inventory_logs")
    os.makedirs(log_dir, exist_ok=True)

    with open(os.path.join(log_dir, "box1.log"), "w") as f:
        f.write("Garbage data from the seller... I swear these people don't know how to pack.\n")
        f.write("Found some wheels. P_ID: P101 | QTY: 15\n")
        f.write("More useless foam peanuts...\n")

    with open(os.path.join(log_dir, "box2.log"), "w") as f:
        f.write("Looks like axles. P_ID: P102 | QTY: 8\n")
        f.write("Some other stuff not on the list. P_ID: P999 | QTY: 100\n")

    with open(os.path.join(log_dir, "box3.txt"), "w") as f:
        f.write("Cabins and mudflaps in this one.\n")
        f.write("P_ID: P104 | QTY: 2\n")
        f.write("P_ID: P106 | QTY: 4\n")

if __name__ == "__main__":
    build_env()
