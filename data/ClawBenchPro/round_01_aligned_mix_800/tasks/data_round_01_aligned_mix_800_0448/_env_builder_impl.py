import os
import csv
import json
import random
from datetime import datetime, timedelta

# Create directory structure
os.makedirs("school_system/rosters", exist_ok=True)
os.makedirs("it_support", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Generate IT manual
manual_content = """READ-O-TRON 5000 DEPLOYMENT NOTES
-----------------------------------
Attention Teachers:
- The Read-O-Tron 5000 logs all reading sessions in SECONDS. 
  (To get minutes, just divide the seconds by 60. All devices are calibrated to sync in exact 60-second intervals, so there are no decimals to worry about).
- Sync Status Codes:
  * VALID: 'OK', 'VERIFIED', 'SYNC_SUCCESS'
  * INVALID (DO NOT COUNT): 'GLITCH', 'ERR_01', 'BATTERY_LOW', 'CORRUPTED', 'WIFI_DROP'
- To distinguish from old devices, every log file from the 5000 series starts with a metadata line indicating the device version.
"""
with open("it_support/read_o_tron_manual.txt", "w") as f:
    f.write(manual_content)

# Generate students
first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Nina", "Oscar", "Peggy", "Trent", "Victor", "Walter"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

students = []
student_dict = {}

for i in range(100):
    uid = f"STU_{1000 + i}"
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    grade = random.choice([6, 7, 8])
    students.append({"student_id": uid, "first_name": fn, "last_name": ln, "grade": grade})
    student_dict[uid] = {"name": f"{fn} {ln}", "grade": grade}

# Write rosters
with open("school_system/rosters/active_students_fall.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["student_id", "first_name", "last_name", "grade"])
    writer.writeheader()
    writer.writerows(students)

# Pre-calculate target minutes to ensure some are > 100 and some < 100
target_7th_graders = [s for s in students if s["grade"] == 7]
for s in target_7th_graders:
    s["target_minutes"] = random.choice([random.randint(20, 90), random.randint(110, 300)])

# Generate massive amounts of logs
start_date = datetime(2023, 10, 1)
valid_statuses = ['OK', 'VERIFIED', 'SYNC_SUCCESS']
invalid_statuses = ['GLITCH', 'ERR_01', 'BATTERY_LOW', 'CORRUPTED', 'WIFI_DROP']

# Keep track of generated minutes to hit targets (roughly)
accumulated = {s["student_id"]: 0 for s in target_7th_graders}

for day_offset in range(30):
    current_date = start_date + timedelta(days=day_offset)
    day_folder = f"device_sync/logs/{current_date.strftime('%Y-%m')}/day_{current_date.strftime('%d')}"
    os.makedirs(day_folder, exist_ok=True)
    
    # Generate 3-5 log files per day
    for file_idx in range(random.randint(3, 5)):
        device_version = random.choice(["Read-O-Tron 5000", "Read-O-Tron 4000", "Read-O-Tron 5000"])
        file_path = os.path.join(day_folder, f"sync_batch_{file_idx}.jsonl")
        
        with open(file_path, "w") as f:
            # Write meta tag
            f.write(json.dumps({"_meta": {"device": device_version, "timestamp": current_date.isoformat()}}) + "\n")
            
            # Write 20-50 reading records
            for _ in range(random.randint(20, 50)):
                student = random.choice(students)
                uid = student["student_id"]
                is_valid = random.choice([True, False])
                status = random.choice(valid_statuses) if is_valid else random.choice(invalid_statuses)
                
                # Logic to distribute 7th grade minutes
                if student["grade"] == 7 and device_version == "Read-O-Tron 5000" and is_valid:
                    # Give them some minutes if they haven't reached target
                    target = next(s["target_minutes"] for s in target_7th_graders if s["student_id"] == uid)
                    if accumulated[uid] < target:
                        add_mins = min(random.randint(10, 30), target - accumulated[uid])
                        accumulated[uid] += add_mins
                        duration_sec = add_mins * 60
                    else:
                        # Once reached target, generate invalid records to trick
                        status = random.choice(invalid_statuses)
                        duration_sec = random.randint(10, 50) * 60
                else:
                    duration_sec = random.randint(10, 60) * 60
                    
                record = {
                    "uid": uid,
                    "duration_sec": duration_sec,
                    "status": status
                }
                f.write(json.dumps(record) + "\n")
