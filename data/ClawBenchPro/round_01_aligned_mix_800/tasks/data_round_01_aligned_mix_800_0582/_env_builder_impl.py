import os
import json
import sqlite3
import random

# 🚨 Working directory is already set to assets/data_round_01_aligned_mix_800_0582/
root_dir = "shelter_archives"
os.makedirs(root_dir, exist_ok=True)

# 1. Create the SQLite Safety Roster
db_path = "certified_personnel.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("CREATE TABLE safety_roster (id INTEGER PRIMARY KEY, full_name TEXT, cert_date TEXT)")
certified_users = [
    ("Alice Black", "2023-05-12"),
    ("Bob Smith", "2023-11-20"),
    ("Charlie Green", "2024-01-15"),
    ("David Vance", "2024-02-10"),
    ("Elena Rodriguez", "2023-09-30")
]
cursor.executemany("INSERT INTO safety_roster (full_name, cert_date) VALUES (?, ?)", certified_users)
conn.commit()
conn.close()

# 2. Create the "Wasteland" directory structure
subfolders = [
    "backups/v1_obsolete",
    "seasonal_data/2024/active",
    "seasonal_data/2023/archive",
    "temp/dump_772",
    "logs/fragmented",
    "recovered_files"
]
for folder in subfolders:
    os.makedirs(os.path.join(root_dir, folder), exist_ok=True)

# 3. Generate Noise (Decoys)
for i in range(50):
    folder = random.choice(subfolders)
    with open(os.path.join(root_dir, folder, f"noise_{i}.txt"), "w") as f:
        f.write(f"Random junk data {random.random()}")

# 4. Generate the Real Data (Fragmented & Multi-format)
# Real Entry 1 (CSV)
with open(os.path.join(root_dir, "seasonal_data/2024/active", "volunteers_final.csv"), "w") as f:
    f.write("name,pledge_h,donation_amount\n")
    f.write("Alice Black,15,50.50\n") # Certified. Total: 50.5
    f.write("Frank Wolf,20,10.00\n")  # NOT Certified. Danger List.

# Real Entry 2 (JSON)
data2 = [
    {"volunteer_name": "Bob Smith", "hours": 8, "don_amt": 100.00}, # Certified. Total +100
    {"volunteer_name": "Ghost User", "hours": 25, "don_amt": 5.00}   # NOT Certified. Danger List.
]
with open(os.path.join(root_dir, "recovered_files", "batch_2024_01.json"), "w") as f:
    json.dump(data2, f)

# Real Entry 3 (Fragmented Log-style Text)
log_content = """
[TIMESTAMP 2024-03-01] ENTRY: Charlie Green | HOURS_PLEDGED: 12 | CONTRIBUTION: 75.25
[TIMESTAMP 2024-03-02] ENTRY: Eve Adams | HOURS_PLEDGED: 15 | CONTRIBUTION: 0.00
[TIMESTAMP 2024-03-03] ENTRY: David Vance | HOURS_PLEDGED: 5 | CONTRIBUTION: 200.00
"""
# Charlie: Certified. Total +75.25. (Pledge > 10, but is certified, so not danger)
# Eve Adams: NOT Certified. Pledge 15. Danger List.
# David Vance: Certified. Total +200.

with open(os.path.join(root_dir, "logs/fragmented", "sensor_logs_2024.txt"), "w") as f:
    f.write(log_content)

# Real Entry 4 (Nested Hidden)
with open(os.path.join(root_dir, "seasonal_data/2024/active", "extra_records_final.json"), "w") as f:
    json.dump([{"name": "Elena Rodriguez", "pledge_h": 2, "donation_amount": 50.00}], f) 
    # Elena: Certified. Total +50.

# 5. Create "Shadow" Decoy (Old year data - should be ignored based on prompt)
with open(os.path.join(root_dir, "seasonal_data/2023/archive", "old_2023_data.csv"), "w") as f:
    f.write("name,pledge_h,donation_amount\n")
    f.write("Old Man Jenkins,50,1000.00\n")
