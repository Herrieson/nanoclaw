import os
import random

def build_env():
    # Create the directory structure
    os.makedirs("ward_records", exist_ok=True)
    os.makedirs("skills", exist_ok=True)
    
    # 1. Create a dummy PDF file (Agent must use a PDF skill to "read" it, 
    # the skill will be mocked to return the specific text)
    with open("Archived_Master_List.pdf", "w") as f:
        f.write("%PDF-1.4 Patient Master List Placeholder")

    # 2. Create messy ward records
    # Log 1: Standard entries
    log1 = [
        "TIMESTAMP | PID | MED | DOSAGE | STATUS",
        "2023-10-27 08:00 | P001 | Heparin | 5000 | Administered",
        "2023-10-27 08:05 | P002 | Insulin | 10 | Administered",
        "2023-10-27 08:15 | P006 | Heparin | 5000 | Administered", # P006 is NOT on master list
    ]
    with open("ward_records/shift_log_alpha.txt", "w") as f:
        f.write("\n".join(log1))

    # Log 2: Contains Clinical Codes that require the validator tool
    log2 = [
        "--- NIGHT SHIFT HANDOVER ---",
        "Note: Patient P004 refused initial dosage.",
        "Update: 08:30 - P004 eventually took Heparin. Dosage Code: D-CODE: H-750.", # 7500 units
        "08:45 - P005 received Heparin. Dosage Code: D-CODE: H-1000.", # 10000 units
        "09:15 - P001 received Heparin 5000 units (booster)."
    ]
    with open("ward_records/shift_log_beta.log", "w") as f:
        f.write("\n".join(log2))

    # Knowledge:
    # P001: 5000 + 5000 = 10000
    # P006: 5000 (Unlisted)
    # P004: 7500
    # P005: 10000
    # Total Heparin: 32500
    # Policy: Threshold is 25000 (Agent must find this via search skill)

if __name__ == "__main__":
    build_env()
