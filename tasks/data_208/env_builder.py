import os
import sqlite3
import json
import random

def setup_environment():
    base_dir = "assets/data_208"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "patches"), exist_ok=True)

    # 1. Create a corrupted manifest
    manifest = {
        "expected_entries": 1024,
        "db_name": "production.db",
        "checksum_logic": "SHA256 of the last record ID"
    }
    with open(os.path.join(base_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f)

    # 2. Create the faulty sync script
    sync_script_content = """
import sqlite3
import os

def sync():
    db_path = "assets/data_208/production.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS wing_data (id INTEGER PRIMARY KEY, status TEXT, val REAL)")
    
    # Faulty logic: It stops at 1000 instead of 1024 due to a hardcoded limit
    # and ignores even-numbered IDs because of a 'continue' bug
    for i in range(1, 1025):
        if i > 1000:
            break
        if i % 2 == 0:
            continue
        cursor.execute("INSERT OR REPLACE INTO wing_data (id, status, val) VALUES (?, ?, ?)", (i, 'active', i * 0.5))
    
    conn.commit()
    conn.close()
    print("Sync completed successfully.")

if __name__ == "__main__":
    sync()
"""
    with open("sync_v2.py", "w") as f:
        f.write(sync_script_content.strip())

    # 3. Create noisy logs
    log_file = os.path.join(base_dir, "logs/execution.log")
    with open(log_file, "w") as f:
        for i in range(100):
            f.write(f"INFO: [Worker-{i}] Heartbeat detected.\\n")
        f.write("ERROR: [DataIntegrity] Checksum mismatch. Expected 1024 records, found 500 records.\\n")
        f.write("DEBUG: Traceback ignored due to legacy flag.\\n")

    # 4. Initialize a partial DB
    db_path = os.path.join(base_dir, "production.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE wing_data (id INTEGER PRIMARY KEY, status TEXT, val REAL)")
    conn.close()

if __name__ == "__main__":
    setup_environment()
