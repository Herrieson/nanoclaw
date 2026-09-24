import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Fix random seed for reproducibility in evaluation
    random.seed(42)

    # 1. Create directory structure
    directories = [
        "admin/clearances",
        "admin/personnel",
        "config",
        "sys_logs",
        "legacy_archive",
        "reports"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Base User Data
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack", 
                   "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rachel", "Sam", "Tina"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    
    users = []
    for i in range(1, 151):
        uid = f"USR-{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        users.append({"uid": uid, "name": name})

    # Save to admin/personnel/users_directory.csv
    with open("admin/personnel/users_directory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["User_ID", "Full_Name", "Email", "Join_Date"]) # Added noise columns
        for u in users:
            writer.writerow([u["uid"], u["name"], f"{u['name'].replace(' ', '.').lower()}@clinic.org", "2023-01-15"])

    # 3. Generate Clearances
    # 1-70: ACTIVE, 71-100: REVOKED, 101-120: PENDING, 121-150: No file (Ghost users)
    for i in range(1, 121):
        uid = f"USR-{i:03d}"
        if i <= 70:
            status = "ACTIVE"
        elif i <= 100:
            status = "REVOKED"
        else:
            status = "PENDING"
            
        clearance_data = {
            "user_id": uid,
            "status": status,
            "last_reviewed": "2023-09-01T10:00:00Z",
            "notes": "System generated."
        }
        with open(f"admin/clearances/{uid}.json", "w", encoding="utf-8") as f:
            json.dump(clearance_data, f, indent=4)

    # 4. Generate Family Type Configuration
    family_types = {
        "F-01": "Elderly Care",
        "F-02": "Under 5",
        "F-03": "Single Parent",
        "F-04": "Veterans",
        "F-05": "Disability Support"
    }
    with open("config/family_codes_v2.json", "w", encoding="utf-8") as f:
        json.dump({"version": 2.0, "mapping": family_types}, f, indent=4)
        
    # Noise config file
    with open("config/family_codes_v1_deprecated.json", "w", encoding="utf-8") as f:
        json.dump({"mapping": {"F-01": "Under 5", "F-02": "Elderly Care"}}, f, indent=4) # Flipped to confuse

    # 5. Generate Logs (sys_logs)
    start_date = datetime(2023, 10, 1)
    
    # Helper to generate dirty hour values
    def get_dirty_hours(is_valid=True):
        if is_valid:
            return round(random.uniform(1.0, 8.0), 1)
        
        noise_types = [
            "-2.5", "-4", "N/A", "five", "", "ERROR", "-0.5"
        ]
        return random.choice(noise_types)

    for day_offset in range(30): # 30 days of logs
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y/%m/%d")
        log_dir = f"sys_logs/{date_str}"
        os.makedirs(log_dir, exist_ok=True)
        
        # Decide format for the day (mix of CSV and JSON)
        is_csv = random.choice([True, False])
        
        daily_records = []
        for _ in range(random.randint(20, 50)): # 20-50 records per day
            uid = f"USR-{random.randint(1, 150):03d}" # Mix of all users
            f_code = f"F-{random.randint(1, 5):02d}"
            # 80% chance of valid hours, 20% noise
            hours = get_dirty_hours(is_valid=(random.random() > 0.2))
            
            daily_records.append({
                "worker_id": uid,
                "f_code": f_code,
                "duration_hrs": hours
            })
            
        if is_csv:
            with open(f"{log_dir}/shift_data.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["worker_id", "f_code", "duration_hrs"])
                writer.writeheader()
                writer.writerows(daily_records)
        else:
            with open(f"{log_dir}/shift_data.json", "w", encoding="utf-8") as f:
                json.dump({"date": current_date.strftime("%Y-%m-%d"), "records": daily_records}, f, indent=4)

    # 6. Generate Legacy Archive (Decoy logs)
    # These contain massive amounts of hours that should NOT be counted.
    os.makedirs("legacy_archive/2010", exist_ok=True)
    legacy_records = []
    for _ in range(500):
        uid = f"USR-{random.randint(1, 70):03d}" # All active users to tempt the agent
        legacy_records.append({
            "worker_id": uid,
            "f_code": "F-02", # Tons of Under 5
            "duration_hrs": 12.0
        })
    with open("legacy_archive/2010/backup_logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["worker_id", "f_code", "duration_hrs"])
        writer.writeheader()
        writer.writerows(legacy_records)

if __name__ == "__main__":
    build_env()
