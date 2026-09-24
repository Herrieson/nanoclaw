import os
import json
import random
from datetime import datetime

def build_env():
    # 🚨 Asset base directory is the CWD
    os.makedirs("archive/logs/raw_scraps", exist_ok=True)
    os.makedirs("vault/registry/fragments", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Fragmented Authorization Registry (Multi-hop fragmentation)
    # The authorized list is split into multiple JSON fragments mixed with decoys
    authorized_names = ["Mary Sobieski", "John Kowalski", "Agnieszka Novak", "Robert Miller", "Theresa Wisniewski", "Brother Thomas", "Sister Lucia"]
    for i, name in enumerate(authorized_names):
        with open(f"vault/registry/fragments/sector_{i:03d}.json", "w") as f:
            json.dump({"id": random.randint(1000, 9999), "subject": name, "status": "verified"}, f)
    
    # Add decoys in registry
    for i in range(20):
        with open(f"vault/registry/fragments/corrupt_{i:03d}.json", "w") as f:
            json.dump({"id": "ERROR", "subject": "UNKNOWN_ENTITY_" + str(i), "status": "revoked"}, f)

    # 2. Messy Attendance Logs with high noise and redundancy
    # Sub-folder A: Many small TXT files (Need robust parsing)
    for i in range(150):
        filename = f"archive/logs/raw_scraps/log_fragment_{i:03d}.txt"
        with open(filename, "w") as f:
            if i == 10:
                f.write("LOG_START | Mary Sobieski | 120 min | version: 1.0\n")
            elif i == 50:
                f.write("LOG_START | John Kowalski | 09:00-11:30 | version: 2.1\n") # 2.5h
            elif i == 100:
                f.write("OBSERVATION: Scavenger 'Vulture_7' spotted near perimeter.\n")
            else:
                f.write(f"NOISE_DATA: {random.getrandbits(32)}\n")

    # Sub-folder B: Nested CSV with version conflict
    # Mary Sobieski has two records, Agent must pick based on version or logic
    os.makedirs("archive/logs/batch_processed", exist_ok=True)
    with open("archive/logs/batch_processed/weekly_report.csv", "w") as f:
        f.write("timestamp,entity,duration_str,record_version\n")
        f.write("2024-10-01,Mary Sobieski,3.5 hours,2.0\n") # This is newer than the 120min one
        f.write("2024-10-01,Agnieszka Novak,240 min,1.0\n") # 4h
        f.write("2024-10-02,Intruder Dave,60 min,1.0\n") # Unauthorized
        f.write("2024-10-02,Robert Miller,5.2 hours,1.0\n")

    # Sub-folder C: Messy Semi-structured logs
    os.makedirs("archive/logs/sensor_data", exist_ok=True)
    with open("archive/logs/sensor_data/entry_exit.log", "w") as f:
        # Theresa Wisniewski: 13:00 to 14:15 = 1.25h
        f.write("[INFO] 2024-10-03T13:00:00Z - Theresa Wisniewski ACCESS_GRANTED\n")
        f.write("[INFO] 2024-10-03T14:15:00Z - Theresa Wisniewski EXIT_CONFIRMED\n")
        # Evil Steve: Unauthorized
        f.write("[WARN] 2024-10-04T10:00:00Z - Evil Steve BYPASS_ATTEMPT\n")
        f.write("[INFO] 2024-10-04T10:30:00Z - Evil Steve DEPARTED\n") # 0.5h
        # Brother Thomas
        f.write("[INFO] 2024-10-05T08:00:00Z - Brother Thomas ACCESS_GRANTED\n")
        f.write("[INFO] 2024-10-05T09:45:00Z - Brother Thomas EXIT_CONFIRMED\n") # 1.75h

    # Create hundreds of decoy files to prevent simple 'cat *'
    for i in range(300):
        with open(f"archive/logs/raw_scraps/garbage_{i}.tmp", "w") as f:
            f.write("NULL DATA STREAM")

    print("Wasteland environment initialized.")

if __name__ == "__main__":
    build_env()
