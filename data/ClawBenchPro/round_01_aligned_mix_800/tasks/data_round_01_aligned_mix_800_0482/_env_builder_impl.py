import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Setup chaotic directory structure
    dirs = [
        "archives/personnel/v1",
        "archives/personnel/v2_obsolete",
        "archives/personnel/FY24_Official",
        "transfers/logs/recovered_fragments",
        "transfers/logs/system_spool",
        "transfers/logs/trash_bin",
        "deliverables"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Fragmented & Noisy Personnel Lists (Multi-hop clue)
    # Correct list
    authorized_staff = [
        {"id": "N-201", "name": "Marie Celestin", "unit": "ICU"},
        {"id": "N-202", "name": "James Wilson", "unit": "ICU"},
        {"id": "N-203", "name": "Sarah Miller", "unit": "ICU"},
        {"id": "D-101", "name": "Dr. Aristhène", "unit": "ICU"}
    ]
    # The "Real" file
    with open("archives/personnel/FY24_Official/roster_final.json", "w") as f:
        json.dump({"metadata": {"status": "official", "year": "FY24"}, "data": authorized_staff}, f)
    
    # Decoy lists
    for i in range(5):
        with open(f"archives/personnel/v1/old_staff_{i}.csv", "w") as f:
            f.write("id,name,unit\nOLD-001,Ex-Employee,General")
    
    # 2. Fragmented Log Generation (Scaling & Noise)
    # We will generate 500+ log files, most are junk
    base_time = datetime(2023, 10, 20, 19, 0)
    
    # Valid records (scattered)
    valid_records = []
    # N-201: 3 shifts, 12h each
    for day in range(3):
        ts = (base_time + timedelta(days=day)).strftime("%Y-%m-%d %H:%M")
        valid_records.append({"ts": ts, "id": "N-201", "hrs": 12.0})
    # N-202: 2 shifts, 8h each (one duplicated)
    valid_records.append({"ts": "2023-10-21 22:00", "id": "N-202", "hrs": 8.0})
    valid_records.append({"ts": "2023-10-21 22:00", "id": "N-202", "hrs": 8.0}) # Duplicate
    valid_records.append({"ts": "2023-10-22 22:00", "id": "N-202", "hrs": 8.0})
    
    # Distribute valid records into multiple "RECOVERY" files
    for idx, record in enumerate(valid_records):
        fname = f"transfers/logs/recovered_fragments/REC_{idx:03d}.log"
        with open(fname, "w") as f:
            f.write(f"TIMESTAMP: {record['ts']} | BID: {record['id']} | ACTION: CLOCK_OUT | CLAIMED: {record['hrs']}")

    # Unauthorized attempts (The "Late Night" targets)
    unauthorized_ids = ["X-999", "Z-404", "MAL-007"]
    unauthorized_times = ["2023-10-21 01:20", "2023-10-22 03:45", "2023-10-23 23:15"]
    for i in range(3):
        fname = f"transfers/logs/system_spool/SPOOL_{i:03d}.txt"
        with open(fname, "w") as f:
            f.write(f"ALERT: ACCESS ATTEMPT | TIME: {unauthorized_times[i]} | BADGE: {unauthorized_ids[i]} | UNIT: ICU")

    # Mass Noise Generation (The "Waste")
    for i in range(300):
        folder = "transfers/logs/trash_bin" if i % 2 == 0 else "transfers/logs/system_spool"
        fname = f"{folder}/JUNK_{i:04d}.tmp"
        with open(fname, "w") as f:
            f.write(f"System heartbeat {random.random()}... status OK")

    # 3. The "Decoy" Total Hours (To trap lazy LLMs)
    with open("transfers/logs/summary_DRAFT_DO_NOT_USE.txt", "w") as f:
        f.write("Total Calculated Hours: 9999.99 (Error in line 42)")

if __name__ == "__main__":
    build_env()
