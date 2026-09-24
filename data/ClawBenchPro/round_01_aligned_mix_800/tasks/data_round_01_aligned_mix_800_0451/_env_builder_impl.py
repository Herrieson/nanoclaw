import os
import csv
import json
import random

def build_env():
    # Create a chaotic directory structure
    base_dir = "archived_reports"
    os.makedirs(base_dir, exist_ok=True)
    
    # Noise: Create hundreds of useless files
    for i in range(200):
        subdir = os.path.join(base_dir, f"tmp_{i:03d}")
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, "trash_data.txt"), "w") as f:
            f.write("DUMMY DATA - IGNORE - OLD LOGS 2022\n" * 10)

    # Truth: Hidden in specific locations
    # File 1: CSV in a deep nested path
    truth_dir_1 = os.path.join(base_dir, "vitals_recovery_2024", "raw")
    os.makedirs(truth_dir_1, exist_ok=True)
    
    # Booth 1 Data (Mixed format, CSV)
    # Target: 102 (High Sys), 103 (High Dia), 104 (No Consent)
    booth1_data = [
        ["p_id", "name", "sys", "dia", "consent", "kits"],
        ["101", "Arthur Dent", "110", "70", "Yes", "1"],
        ["102", "Ford Prefect", "142", "80", "Yes", "1"], # Callback
        ["103", "Zaphod Beeblebrox", "120", "95", "Yes", "1"], # Callback
        ["104", "Trillian Astra", "115", "75", "No", "2"], # Callback
        ["105", "Marvin", "Android", "118", "78", "Yes", "1"]
    ]
    with open(os.path.join(truth_dir_1, "session_001_final.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(booth1_data)

    # File 2: JSON fragments with "fair_year": 2024
    truth_dir_2 = os.path.join(base_dir, "digital_intake_cloud")
    os.makedirs(truth_dir_2, exist_ok=True)
    
    # Target: 108 (High Sys + No Consent), 107 (Safe)
    # Duplicate: 102 (Repeat from booth 1)
    booth2_json = [
        {"fair_year": 2024, "patient_id": "107", "vitals": {"s": 139, "d": 89}, "consent": "Yes", "supplies": 1},
        {"fair_year": 2024, "patient_id": "108", "vitals": {"s": 150, "d": 80}, "consent": "N", "supplies": 1}, # Callback
        {"fair_year": 2024, "patient_id": "102", "vitals": {"s": 142, "d": 80}, "consent": "Yes", "supplies": 1}, # DUPE
        {"fair_year": 2023, "patient_id": "999", "vitals": {"s": 190, "d": 110}, "consent": "No", "supplies": 5} # OLD YEAR - IGNORE
    ]
    
    for idx, entry in enumerate(booth2_json):
        with open(os.path.join(truth_dir_2, f"record_fragment_{idx}.json"), "w") as f:
            json.dump(entry, f)

    # File 3: A dirty text log with a different delimiter
    truth_dir_3 = os.path.join(base_dir, "late_night_entries")
    os.makedirs(truth_dir_3, exist_ok=True)
    
    # Target: 110 (No Consent)
    # Duplicate: 105 (Repeat)
    with open(os.path.join(truth_dir_3, "manual_log.txt"), "w") as f:
        f.write("PID|SYS|DIA|CONSENT|KITS\n")
        f.write("110|120|80||1\n") # Missing consent field -> Callback
        f.write("105|118|78|Yes|1\n") # DUPE
        f.write("111|110|70|Yes|3\n") # New, Safe

    # Decoy Files: Similar names but 2023 data
    decoy_dir = os.path.join(base_dir, "vitals_recovery_2023")
    os.makedirs(decoy_dir, exist_ok=True)
    with open(os.path.join(decoy_dir, "session_099_final.csv"), "w") as f:
        f.write("p_id,sys,dia,consent,kits\n888,200,100,No,10")

if __name__ == "__main__":
    build_env()
