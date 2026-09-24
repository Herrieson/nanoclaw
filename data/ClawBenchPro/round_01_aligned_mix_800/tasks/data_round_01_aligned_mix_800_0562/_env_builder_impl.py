import os
import json
import csv
import random
from datetime import datetime, timedelta

def generate_random_time(start_hour, end_hour):
    h = random.randint(start_hour, end_hour)
    m = random.choice([0, 15, 30, 45])
    return f"{h:02d}:{m:02d}"

def calculate_hours(in_time, out_time):
    fmt = "%H:%M"
    td = datetime.strptime(out_time, fmt) - datetime.strptime(in_time, fmt)
    return td.total_seconds() / 3600.0

def build_env():
    random.seed(42) # For reproducibility
    
    # 1. Create Directories
    os.makedirs('db', exist_ok=True)
    os.makedirs('scans/checkins', exist_ok=True)
    os.makedirs('admin_records', exist_ok=True)
    os.makedirs('final_docs', exist_ok=True)
    
    # 2. Generate Roster
    first_names = ["Leo", "Mia", "Zoe", "Carlos", "Sam", "Alex", "Chloe", "Emma", "Oliver", "Noah", 
                   "Ava", "Elijah", "Charlotte", "Harper", "Liam", "Amelia", "Evelyn", "Mateo", "Luna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    
    roster = []
    student_ids = []
    for i in range(1, 151):
        s_id = f"STU{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        grade = str(random.randint(4, 8))
        roster.append([s_id, name, grade])
        student_ids.append(s_id)
        
    with open('db/roster.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'FullName', 'GradeLevel', 'Status'])
        for r in roster:
            writer.writerow([r[0], r[1], r[2], 'Active'])
            
    # 3. Generate Slip Transactions (The running diary)
    # We will simulate parents submitting, then some withdrawing.
    # We generate a list of events with timestamps, then sort them to simulate a log.
    log_events = []
    base_date = datetime(2023, 9, 1, 8, 0, 0)
    
    # Give most students an initial status
    final_statuses = {}
    for s_id in student_ids:
        # 80% chance to submit something
        if random.random() < 0.8:
            ts = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 10), minutes=random.randint(0, 59))
            status = random.choice(['Signed', 'Pending', 'Signed', 'Signed'])
            log_events.append((ts, s_id, status))
            final_statuses[s_id] = status
            
    # Add some dramatic changes (Revokes, or late signs)
    for _ in range(40):
        s_id = random.choice(student_ids)
        ts = base_date + timedelta(days=random.randint(31, 40), hours=random.randint(0, 10), minutes=random.randint(0, 59))
        status = random.choice(['Void', 'Signed', 'Pending'])
        log_events.append((ts, s_id, status))
        final_statuses[s_id] = status

    log_events.sort(key=lambda x: x[0]) # sort by timestamp
    
    with open('admin_records/slip_transactions.log', 'w', encoding='utf-8') as f:
        f.write("=== ADMIN SLIP TRACKING LOG ===\n")
        f.write("NOTE: Parents are indecisive. Only the LAST entry for a student counts.\n\n")
        for ts, s_id, status in log_events:
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            admin_user = random.choice(['Admin_Jill', 'Principal_Bob', 'System_Auto'])
            f.write(f"[{ts_str}] UPDATE: Record for {s_id} updated by {admin_user} -> Status: {status}\n")

    # 4. Generate Check-in Scans (The fragments & noise)
    # We will generate ~300 json files. 
    # Some will be for EcoPark, some for School_Yard. Some will be corrupted.
    file_counter = 1
    
    # Let's decide who actually attended EcoPark
    eco_attendees = random.sample(student_ids, 85)
    
    # Create EcoPark valid checkins
    for i in range(0, len(eco_attendees), 5):
        batch = eco_attendees[i:i+5]
        records = []
        for s_id in batch:
            in_t = generate_random_time(7, 9)
            out_t = generate_random_time(11, 14)
            records.append({"id": s_id, "in": in_t, "out": out_t})
            
        payload = {
            "device": f"Terminal_{random.randint(1,5)}",
            "date": "2023-10-14",
            "location": "EcoPark",
            "records": records
        }
        with open(f'scans/checkins/scan_batch_{file_counter}.json', 'w') as f:
            json.dump(payload, f, indent=2)
        file_counter += 1

    # Create School_Yard (Noise) checkins
    school_yard_attendees = random.sample(student_ids, 60)
    for i in range(0, len(school_yard_attendees), 6):
        batch = school_yard_attendees[i:i+6]
        records = []
        for s_id in batch:
            in_t = generate_random_time(15, 16)
            out_t = generate_random_time(17, 18)
            records.append({"id": s_id, "in": in_t, "out": out_t})
            
        payload = {
            "device": f"Terminal_{random.randint(1,5)}",
            "date": "2023-10-02",
            "location": "School_Yard",
            "records": records
        }
        with open(f'scans/checkins/scan_batch_{file_counter}.json', 'w') as f:
            json.dump(payload, f, indent=2)
        file_counter += 1

    # Create Corrupted Files (Noise)
    for _ in range(15):
        with open(f'scans/checkins/scan_batch_{file_counter}_corrupt.json', 'w') as f:
            f.write('{"device": "Terminal_Offline", "date": "2023-10-14", "location": "EcoPark", "records": [{"id": "STU0')
        file_counter += 1

if __name__ == '__main__':
    build_env()
