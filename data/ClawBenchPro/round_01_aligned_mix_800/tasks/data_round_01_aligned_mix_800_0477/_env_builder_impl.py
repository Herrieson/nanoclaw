import os
import json
import csv
import random

def build_env():
    # Base structure
    root = "archive"
    os.makedirs(f"{root}/registry", exist_ok=True)
    os.makedirs(f"{root}/claims", exist_ok=True)
    os.makedirs(f"{root}/dispensing_logs", exist_ok=True)
    os.makedirs(f"{root}/DEPRECATED", exist_ok=True)

    # 1. Official Roster - Fragmented
    staff = [
        ("RN-01", "Bernice Thompson"), ("RN-02", "Althea Richards"),
        ("RN-03", "Cedric Miller"), ("RN-04", "Darnell Williams"),
        ("RN-05", "Elena Vance"), ("RN-06", "Garrick Thorne")
    ]
    # Split roster into multiple CSVs
    for i, chunk in enumerate([staff[:3], staff[3:]]):
        with open(f"{root}/registry/roster_part_{i}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name"])
            writer.writerows(chunk)

    # 2. Overtime Claims - Fragmented & Noisy
    # Valid Claims (2024-Q3)
    valid_claims = [
        ("Bernice Thompson", 15.5, "2024-Q3"),
        ("Bernice Thompson", 26.0, "2024-Q3"), # Total 41.5 -> CRITICAL
        ("Althea Richards", 12.0, "2024-Q3"),
        ("Marcus Vane", 10.0, "2024-Q3"),      # GHOST 1
        ("Elena Vance", 5.0, "2024-Q3"),
    ]
    
    # Noise: Old periods, VOID files, and Deprecated data
    noise_data = [
        ("Cedric Miller", 45.0, "2023-Q4"),     # Wrong Period
        ("Darnell Williams", 10.0, "2024-Q3"),  # In a _VOID_ file later
        ("Sheila Reed", 100.0, "2024-Q3"),      # In DEPRECATED
    ]

    for i, (name, hours, period) in enumerate(valid_claims):
        with open(f"{root}/claims/claim_rec_{100+i}.json", "w") as f:
            json.dump({"staff_name": name, "hours": hours, "period": period}, f)

    # VOID File Noise
    with open(f"{root}/claims/claim_rec_999_VOID_.json", "w") as f:
        json.dump({"staff_name": "Darnell Williams", "hours": 99.0, "period": "2024-Q3"}, f)

    # Deprecated Noise
    with open(f"{root}/DEPRECATED/old_records.json", "w") as f:
        json.dump({"staff_name": "Sheila Reed", "hours": 20.0, "period": "2024-Q3"}, f)

    # 3. Dispensing Logs - High volume text noise
    meds = ["Stims", "Rad-Away", "Morphine", "Antibiotics"]
    for i in range(200):
        name = random.choice([s[1] for s in staff] + ["Unknown Scavenger", "Ghost-7"])
        # Ensure "Ghost-7" is definitely a ghost
        if i == 50: name = "Ghost-7" 
        
        filename = f"{root}/dispensing_logs/log_event_{i:03d}.txt"
        with open(filename, "w") as f:
            f.write(f"TIMESTAMP: 2024-08-15 | USER: {name} | ACTION: Dispensed {random.choice(meds)}")

    # 4. Decoy/Garbage files
    for i in range(10):
        with open(f"{root}/claims/temp_cache_{i}.tmp", "w") as f:
            f.write("CORRUPT DATA SEGMENT " * 10)

if __name__ == "__main__":
    build_env()
