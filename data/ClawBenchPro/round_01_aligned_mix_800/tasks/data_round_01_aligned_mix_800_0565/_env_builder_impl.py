import os
import json
import csv
import random

def build_env():
    root = "archive_root"
    os.makedirs(root, exist_ok=True)

    meds = ["Lisinopril", "Amoxicillin", "Metformin", "Atorvastatin", "Ibuprofen"]
    active_hash = "2024_ACTIVE"
    
    # 1. Create a deep, confusing directory structure
    subfolders = [
        f"{active_hash}/terminal_1",
        f"{active_hash}/terminal_2/logs",
        "backups/2023/recovered",
        "temp/test_runs",
        "trash/shredded_docs"
    ]
    
    for sub in subfolders:
        os.makedirs(os.path.join(root, sub), exist_ok=True)

    # 2. Generate VALID data (Scattered)
    # Target Amoxicillin Anomalies: P-ERR-99 (500mg), P-ERR-102 (250mg)
    
    # Valid File A: JSON fragment in active folder
    valid_a = {
        "records": [
            {"pid": "P-001", "med": "Lisinopril", "dose": 10, "qty": 30, "meta": "STATUS: VERIFIED"},
            {"pid": "P-ERR-99", "med": "Amoxicillin", "dose": 500, "qty": 10, "meta": "STATUS: VERIFIED"} # ANOMALY
        ]
    }
    with open(os.path.join(root, active_hash, "terminal_1", "enc_001.json"), "w") as f:
        json.dump(valid_a, f)

    # Valid File B: CSV with pipe separator in active folder
    valid_b = [
        "Patient_ID|Medication|Dose_mg|Qty_Dispensed",
        "P-002|Amoxicillin|100|20",
        "P-003|Atorvastatin|20|90"
    ]
    with open(os.path.join(root, active_hash, "terminal_2/logs", "daily.txt"), "w") as f:
        f.write("\n".join(valid_b))

    # Valid File C: Raw text with "VERIFIED" flag in a "wrong" folder
    valid_c = """
    LOG_START
    ENTRY: P-ERR-102, Amoxicillin, 250mg, QTY: 5
    ENTRY: P-005, Metformin, 500mg, QTY: 60
    STATUS: VERIFIED
    LOG_END
    """ # ANOMALY P-ERR-102
    with open(os.path.join(root, "backups/2023/recovered", "salvage_record.log"), "w") as f:
        f.write(valid_c)

    # 3. Generate NOISE (Large scale decoys)
    # These look like real data but lack the VERIFIED flag or the correct path hash
    for i in range(50):
        filename = f"old_record_{i}.csv"
        # decoy data
        with open(os.path.join(root, "trash/shredded_docs", filename), "w") as f:
            f.write("Patient_ID,Medication,Dose_mg,Qty_Dispensed\n")
            f.write(f"P-OLD-{i},Amoxicillin,1000,100\n") # Fake anomaly, should be ignored

    for i in range(20):
        filename = f"test_data_{i}.json"
        with open(os.path.join(root, "temp/test_runs", filename), "w") as f:
            json.dump({"pid": "DEBUG", "med": "Amoxicillin", "dose": 999, "qty": 0}, f)

    # 4. A subtle clue file
    with open(os.path.join(root, "README_FIRST.txt"), "w") as f:
        f.write("System Migration Note: Only files with 'STATUS: VERIFIED' or inside the '2024_ACTIVE' hash are legally binding for the audit.")

if __name__ == "__main__":
    build_env()
