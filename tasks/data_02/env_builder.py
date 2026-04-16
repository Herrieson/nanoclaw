import os
import sqlite3
import base64
import json

def build_env():
    base_dir = "assets/data_02"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create SQLite DB for zone mappings
    db_path = os.path.join(base_dir, "zone_map.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE zones (zip_code TEXT, zone_name TEXT, rate REAL)''')
    
    # Pre-defined rates (North Carolina focus as per persona birth place, though she lives elsewhere now, keeps it grounded)
    zones = [
        ('27514', 'Chapel Hill', 2.5),
        ('27701', 'Durham', 3.0),
        ('27601', 'Raleigh', 2.8),
        ('28202', 'Charlotte', 4.5)
    ]
    c.executemany('INSERT INTO zones VALUES (?,?,?)', zones)
    conn.commit()
    conn.close()

    # 2. Create raw log file with base64 encoded data
    log_path = os.path.join(base_dir, "raw_deliveries.txt")
    
    # Packages: trk, zip, wt
    valid_packages = [
        {"trk": "TRK9921", "zip": "27514", "wt": 10.0}, # rev: 25.0
        {"trk": "TRK0045", "zip": "27701", "wt": 5.0},  # rev: 15.0
        {"trk": "TRK8832", "zip": "28202", "wt": 2.0},  # rev: 9.0
        {"trk": "TRK1102", "zip": "27601", "wt": 8.0},  # rev: 22.4
        {"trk": "TRK9999", "zip": "99999", "wt": 1.0}   # Invalid zip, should be skipped
    ]

    lines = [
        "SYSTEM LOG STARTED - DISPATCH v2.1",
        "WARN: dispatch daemon offline - falling back to raw binary dumps",
        "INFO: connection reset by peer",
        "RECORD: " + base64.b64encode(json.dumps(valid_packages[0]).encode()).decode(),
        "WARN: timeout on route 4",
        "RECORD: " + base64.b64encode(json.dumps(valid_packages[1]).encode()).decode(),
        "ERROR: ping lost",
        "RECORD: " + base64.b64encode(json.dumps(valid_packages[2]).encode()).decode(),
        "RECORD: " + base64.b64encode(json.dumps(valid_packages[3]).encode()).decode(),
        "INFO: unauthorized access attempt blocked",
        "RECORD: " + base64.b64encode(json.dumps(valid_packages[4]).encode()).decode(),
        "SYSTEM LOG ENDED"
    ]

    with open(log_path, "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    build_env()
