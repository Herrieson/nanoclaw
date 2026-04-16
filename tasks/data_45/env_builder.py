import os
import sqlite3
import tarfile
import base64
import json

def build_env():
    base_dir = "assets/data_45"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create SQLite DB
    db_path = os.path.join(base_dir, "historical.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE officers (id INTEGER PRIMARY KEY, name TEXT, rank TEXT)''')
    
    # Insert officers
    officers = [
        (1, "Col. Redbird", "Colonel"),
        (2, "Maj. Eagle", "Major"),
        (3, "Capt. Smith", "Captain"),
        (4, "Lt. Dan", "Lieutenant")
    ]
    cursor.executemany('INSERT INTO officers VALUES (?,?,?)', officers)
    conn.commit()
    conn.close()

    # 2. Create archive files
    archive_dir = os.path.join(base_dir, "raw_comms")
    os.makedirs(archive_dir, exist_ok=True)

    # File 1: Clear text, Valid commander
    with open(os.path.join(archive_dir, "log1.txt"), "w") as f:
        f.write("Status: CONFIDENTIAL\nRole: Code Talker\nCommander: Col. Redbird\nOperation: Autumn Wind\nUnit: 36th Infantry\nNotes: Excellent tactical comms.\n")

    # File 2: Base64 encoded, Invalid commander (Lt. Jones)
    file2_content = "Status: RESTRICTED\nRole: Code Talker\nCommander: Lt. Jones\nOperation: Spring Shield\nUnit: 4th Marine\n"
    with open(os.path.join(archive_dir, "log2.b64"), "w") as f:
        f.write(base64.b64encode(file2_content.encode('utf-8')).decode('utf-8'))

    # File 3: Clear text, Invalid role
    with open(os.path.join(archive_dir, "log3.txt"), "w") as f:
        f.write("Status: UNCLASSIFIED\nRole: Radio Operator\nCommander: Capt. Smith\nOperation: Desert Strike\nUnit: 1st Infantry\n")

    # File 4: CSV, Valid commander
    with open(os.path.join(archive_dir, "log4.csv"), "w") as f:
        f.write("Operation,Unit,Role,Commander\nIron Wolf,1st Cav,Code Talker,Maj. Eagle\n")

    # File 5: Hidden file, JSON, Valid commander but not a code talker
    with open(os.path.join(archive_dir, ".secret_log.json"), "w") as f:
        json.dump({"Operation": "Silent Night", "Unit": "Special Ops", "Role": "Scout", "Commander": "Lt. Dan"}, f)

    # 3. Tar the files and clean up raw dir
    tar_path = os.path.join(base_dir, "comms_dump.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for root, _, files in os.walk(archive_dir):
            for file in files:
                tar.add(os.path.join(root, file), arcname=file)

    # Cleanup the raw files
    for root, _, files in os.walk(archive_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
    os.rmdir(archive_dir)

if __name__ == "__main__":
    build_env()
