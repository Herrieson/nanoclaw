import os
import sqlite3
import random

def build_env():
    base_dir = "assets/data_256/lab_data"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Build SQLite DB
    db_path = os.path.join(base_dir, "compounds.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE targets (id INTEGER PRIMARY KEY, name TEXT, mw REAL, expected_rt REAL)''')
    
    # Insert data (includes a trap: Compound_Z has negative MW)
    compounds = [
        ("Compound_X", 342.5, 4.50),
        ("Compound_Y", 410.1, 5.90),
        ("Compound_Z", -10.0, 2.15), 
        ("Compound_W", 250.0, 8.10),
        ("Compound_V", 180.2, 10.50)
    ]
    c.executemany('INSERT INTO targets (name, mw, expected_rt) VALUES (?, ?, ?)', compounds)
    conn.commit()
    conn.close()
    
    # 2. Build Messy Log File
    log_path = os.path.join(base_dir, "raw_hplc_logs.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("[DEBUG] Instrument initialized. Calibration OK.\n")
        f.write("\x00\x01\x02Corrupted Header Bytes\x03\x04\n")
        f.write("[INFO] Starting run for Batch B101\n")
        f.write("Batch: B101 | RT: 4.45 min | Area: 8000\n") # Matches X
        f.write("Batch: B101 | RT: 2.15 min | Area: 2000\n") # Matches Z (but Z is invalid)
        f.write("Batch: B101 | RT: 1.05 min | Area: 400\n")  # Area <= 500, should be ignored
        f.write("ERROR: buffer overflow at 0x8FA4\n")
        
        f.write("[INFO] Starting run for Batch B102\n")
        f.write("Batch: B102 | RT: 5.85 min | Area: 6000\n") # Matches Y
        f.write("Batch: B102 | RT: 8.05 min | Area: 3000\n") # Matches W
        f.write("Batch: B102 | RT: 1.00 min | Area: 1000\n") # No match, but area > 500
        f.write("Batch: B102 | RT: 3.33 min | Area: 250\n")  # Area <= 500, ignore
        f.write("System warning: pressure low.\n")

if __name__ == "__main__":
    build_env()
