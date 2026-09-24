import os
import csv
import json
import random
import yaml

def create_dirty_csv(path, records, tag="[FINAL]"):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["UID", "Full_Name", "Status", "Years_Old", "Dietary_Notes"])
        for rec in records:
            writer.writerow(rec)

def main():
    # 1. Structure: Fragmentation & Deep Nesting
    base_dirs = ["archive_depot/sector_7/logs", "archive_depot/sector_3/temp", "corrupted_sectors/recovery_alpha"]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)
    
    os.makedirs("protocols", exist_ok=True)
    os.makedirs("system_trash", exist_ok=True)

    # 2. Logic Pieces: The Rules (YAML)
    exhibit_rules = {
        "exhibit_mappings": [
            {"name": "Potawatomi_Crafts", "range": [5, 10]},
            {"name": "Navajo_Code_Talkers", "range": [11, 17]}
        ]
    }
    with open("protocols/event_rules_v4_FINAL.yaml", "w") as f:
        yaml.dump(exhibit_rules, f)

    # 3. Noise & Decoys: Massive amount of trash
    for i in range(50):
        trash_path = f"system_trash/garbage_{i}.log"
        with open(trash_path, "w") as f:
            f.write(f"Random junk data {random.random()}")

    # 4. Data Fragments (The Real Info)
    # Target: 5-17 Dependents
    real_data_1 = [
        ["ID-992", "Little Bear", "Dependent", "6", "None"],
        ["ID-102", "Sgt. Miller", "Active Duty", "30", "Gluten Free"], # Ignore
        ["ID-441", "Alice Morningstar", "Dependent", "12", "None"]
    ]
    real_data_2 = [
        ["ID-005", "Cree Summer", "Dependent", "17", "Peanuts"], # Special Chow
        ["ID-882", "Billy Two-Hats", "Dependent", "5", "none"], # Standard MRE (case check)
        ["ID-771", "Old Man Logan", "Active Duty", "90", "Soft Food"] # Ignore
    ]
    real_data_3 = [
        ["ID-223", "Sky Walker", "Dependent", "10", "Shellfish"], # Special Chow
        ["ID-119", "Baby Yoda", "Dependent", "3", "Milk"], # Too young
        ["ID-445", "T-1000", "Dependent", "19", "None"] # Too old
    ]

    create_dirty_csv("archive_depot/sector_7/logs/roster_fragment_01_[FINAL].csv", real_data_1)
    create_dirty_csv("corrupted_sectors/recovery_alpha/node_88_data_[FINAL].csv", real_data_2)
    create_dirty_csv("archive_depot/sector_3/temp/rebuilt_export_[FINAL].csv", real_data_3)

    # 5. Bait/Stale Files (Should be ignored)
    stale_data = [["ID-999", "Ghost User", "Dependent", "10", "None"]]
    create_dirty_csv("archive_depot/sector_7/logs/roster_fragment_01_[STALE].csv", stale_data)
    create_dirty_csv("archive_depot/sector_7/logs/backup_old.csv", stale_data)

    # Add a decoy rule file
    with open("protocols/event_rules_v1_DEPRECATED.yaml", "w") as f:
        yaml.dump({"rules": "invalid"}, f)

if __name__ == "__main__":
    main()
