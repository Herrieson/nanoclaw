import os
import sqlite3

def build_env():
    base_dir = "assets/data_244"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create SQLite DB
    db_path = os.path.join(base_dir, "inventory.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE inventory (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            stock_quantity INTEGER,
            vendor_code TEXT
        )
    ''')
    
    initial_data = [
        ("P100", "Widget A", 150, "V01"),
        ("P101", "Widget B", 80, "V02"),
        ("P102", "Gearbox", 30, "V03"),
        ("P103", "Circuit Board", 200, "V04"),
        ("P104", "Steel Frame", 10, "V05"),
        ("P105", "Sensor Unit", 45, "V01"),
    ]
    c.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?)", initial_data)
    conn.commit()
    conn.close()
    
    # 2. Create Scanner Logs
    logs_dir = os.path.join(base_dir, "scanner_logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    log1_content = """2023-10-25 08:15:00 | ACTION: IN | PID: P100 | QTY: 50 | VENDOR: V01
2023-10-25 09:00:22 | ACTION: OUT | PID: P102 | QTY: 15 | VENDOR: V03
2023-10-25 09:30:10 | ACTION: IN | PID: P104 | QTY: 100 | VENDOR: V05
"""
    log2_content = """2023-10-25 10:05:00 | ACTION: OUT | PID: P101 | QTY: 20 | VENDOR: V02
2023-10-25 11:20:00 | ACTION: IN | PID: P105 | QTY: 30 | VENDOR: V06
2023-10-25 13:45:00 | ACTION: IN | PID: P102 | QTY: 5 | VENDOR: V03
2023-10-25 14:00:00 | ACTION: OUT | PID: P103 | QTY: 190 | VENDOR: V04
"""
    
    with open(os.path.join(logs_dir, "scanner_morning.txt"), "w") as f:
        f.write(log1_content)
        
    with open(os.path.join(logs_dir, "scanner_afternoon.txt"), "w") as f:
        f.write(log2_content)
        
    # 3. Create blacklist
    blacklist_content = "V03\nV05\nV08\n"
    with open(os.path.join(base_dir, "blacklist.txt"), "w") as f:
        f.write(blacklist_content)

if __name__ == "__main__":
    build_env()
