import os
import csv
import random

def build_env():
    # Create the directory structure
    os.makedirs("ward_records", exist_ok=True)
    
    # 1. Create Patient Master List
    patients = [
        ["Patient_ID", "Name", "Room", "Status"],
        ["P001", "John Doe", "401", "Admitted"],
        ["P002", "Jane Smith", "402", "Admitted"],
        ["P003", "Alice Brown", "403", "Discharged"],
        ["P004", "Bob Wilson", "404", "Admitted"],
        ["P005", "Charlie Davis", "405", "Admitted"]
    ]
    with open("Patient_Master_List.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(patients)

    # 2. Create messy ward records (logs)
    # Log 1: Standard entries
    log1 = [
        "TIMESTAMP | PID | MED | DOSAGE | STATUS",
        "2023-10-27 08:00 | P001 | Heparin | 5000 | Administered",
        "2023-10-27 08:05 | P002 | Insulin | 10 | Administered",
        "2023-10-27 08:15 | P006 | Heparin | 5000 | Administered", # P006 is NOT on master list (Discrepancy)
    ]
    with open("ward_records/shift_log_alpha.txt", "w") as f:
        f.write("\n".join(log1))

    # Log 2: Messy entries and more Heparin
    log2 = [
        "--- NIGHT SHIFT HANDOVER ---",
        "Note: Patient P004 refused initial dosage.",
        "Update: 08:30 - P004 eventually took Heparin 7500 units.",
        "08:45 - P005 received Heparin 10000 units.",
        "Error Log: System glitch at 09:00.",
        "09:15 - P001 received Heparin 5000 units (booster)."
    ]
    with open("ward_records/shift_log_beta.log", "w") as f:
        f.write("\n".join(log2))

    # Note: P003 (Alice Brown) is on list but missed 0800 meds (Discrepancy)
    # Total Heparin: 5000 (P001) + 5000 (P006) + 7500 (P004) + 10000 (P005) + 5000 (P001) = 32500
    # Threshold 25000 exceeded.

if __name__ == "__main__":
    build_env()
