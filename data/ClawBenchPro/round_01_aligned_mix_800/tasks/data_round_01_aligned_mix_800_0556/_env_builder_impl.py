import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 1. Base Directories
    os.makedirs("messy_desk/contracts", exist_ok=True)
    os.makedirs("messy_desk/receipts", exist_ok=True)
    os.makedirs("family_planning", exist_ok=True)
    
    # 2. Clue: Employee ID mapping
    contracts = {
        "company": "El Sombrero Restaurant",
        "employees": [
            {"name": "Maria", "emp_id": "EMP-001", "role": "Waitress", "rate": 12.00},
            {"name": "Elena", "emp_id": "EMP-002", "role": "Cashier", "rate": 14.50},
            {"name": "Carlos", "emp_id": "EMP-003", "role": "Cook", "rate": 16.00}
        ]
    }
    with open("messy_desk/contracts/active_staff_2023.json", "w") as f:
        json.dump(contracts, f, indent=4)

    # Distraction files
    with open("messy_desk/receipts/grocery_01.txt", "w") as f:
        f.write("Supermercado\nMilk: $3.50\nEggs: $4.20\nTotal: $7.70\n")
    with open("messy_desk/receipts/book_receipt.txt", "w") as f:
        f.write("Libreria Mexico\nOctavio Paz Book - $15.99\n")

    # 3. Scale & Fragmentation: Massive Shift Records
    base_shift_dir = "restaurant_records/shifts"
    
    # Pre-defined ground truth shifts for Elena (EMP-002) in October 2023
    elena_oct_shifts = [
        # Shift 1: Mon, Oct 2 - 6 hours (valid)
        {"id": "S-1001", "date": "2023-10-02", "start": "09:00", "end": "15:00", "versions": [
            {"v": 1, "status": "active"}
        ]},
        # Shift 2: Thu, Oct 5 - Conflict!
        {"id": "S-1002", "date": "2023-10-05", "start": "12:00", "end": "14:00", "versions": [
            {"v": 1, "status": "active"}, 
            {"v": 2, "status": "active", "start": "14:00", "end": "18:00"} # v2 overrides v1, overlaps 15:00-17:00 (4 hours)
        ]},
        # Shift 3: Tue, Oct 10 - 6 hours (valid)
        {"id": "S-1003", "date": "2023-10-10", "start": "10:00", "end": "16:00", "versions": [
            {"v": 1, "status": "active"}
        ]},
        # Shift 4: Thu, Oct 12 - Boundary, no conflict (Ends exactly at 15:00)
        {"id": "S-1004", "date": "2023-10-12", "start": "13:00", "end": "15:00", "versions": [
            {"v": 1, "status": "active"} # 2 hours
        ]},
        # Shift 5: Wed, Oct 18 - Cancelled eventually
        {"id": "S-1005", "date": "2023-10-18", "start": "08:00", "end": "14:00", "versions": [
            {"v": 1, "status": "active"},
            {"v": 2, "status": "cancelled"} # 0 hours
        ]},
        # Shift 6: Thu, Oct 19 - Conflict!
        {"id": "S-1006", "date": "2023-10-19", "start": "16:00", "end": "20:00", "versions": [
            {"v": 1, "status": "active"} # overlaps 15:00-17:00 (4 hours)
        ]},
        # Shift 7: Thu, Oct 26 - Boundary, no conflict (Starts exactly at 17:00)
        {"id": "S-1007", "date": "2023-10-26", "start": "17:00", "end": "21:00", "versions": [
            {"v": 1, "status": "active"} # 4 hours
        ]}
    ]
    # Total valid hours for Elena in Oct: 6 + 4 + 6 + 2 + 0 + 4 + 4 = 26 hours.
    # Total Expected Pay = 26 * 14.50 = $377.00
    # Conflict Dates = 2023-10-05, 2023-10-19

    all_shifts_to_write = []

    # Add Elena's truth data
    for s in elena_oct_shifts:
        for ver in s["versions"]:
            start = ver.get("start", s["start"])
            end = ver.get("end", s["end"])
            all_shifts_to_write.append({
                "shift_id": s["id"],
                "emp_id": "EMP-002",
                "date": s["date"],
                "start_time": start,
                "end_time": end,
                "version": ver["v"],
                "status": ver["status"]
            })

    # Generate massive noise data (other employees, other months, cancelled shifts)
    random.seed(42)
    start_date = datetime(2023, 8, 1)
    end_date = datetime(2023, 11, 30)
    
    current_shift_id = 2000
    for _ in range(400):
        # Random date
        days_offset = random.randint(0, (end_date - start_date).days)
        target_date = start_date + timedelta(days=days_offset)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Pick employee (mostly Maria and Carlos, sometimes Elena but NOT in October)
        if target_date.month == 10:
            emp_id = random.choice(["EMP-001", "EMP-003"])
        else:
            emp_id = random.choice(["EMP-001", "EMP-002", "EMP-003"])
            
        shift_id = f"S-{current_shift_id}"
        current_shift_id += 1
        
        start_hour = random.randint(7, 18)
        duration = random.randint(4, 8)
        start_time = f"{start_hour:02d}:00"
        end_time = f"{start_hour+duration:02d}:00"
        
        # Determine versions
        num_versions = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        for v in range(1, num_versions + 1):
            status = "active"
            if v == num_versions and random.random() < 0.15:
                status = "cancelled"
            
            # Slight time shift in newer versions
            if v > 1 and status == "active":
                start_hour += random.choice([-1, 1])
                start_time = f"{max(7, start_hour):02d}:00"
                end_time = f"{max(11, start_hour+duration):02d}:00"
            
            all_shifts_to_write.append({
                "shift_id": shift_id,
                "emp_id": emp_id,
                "date": date_str,
                "start_time": start_time,
                "end_time": end_time,
                "version": v,
                "status": status
            })

    # Write all shifts to heavily fragmented directory structure
    for record in all_shifts_to_write:
        # Fragment by Year / Month / Week
        date_obj = datetime.strptime(record["date"], "%Y-%m-%d")
        year = date_obj.strftime("%Y")
        month = date_obj.strftime("%m")
        week = f"week_{date_obj.isocalendar()[1]}"
        
        dir_path = os.path.join(base_shift_dir, year, month, week)
        os.makedirs(dir_path, exist_ok=True)
        
        # Add random noise to filename
        filename = f"record_{record['shift_id']}_v{record['version']}_{random.randint(1000,9999)}.json"
        
        with open(os.path.join(dir_path, filename), "w") as f:
            json.dump(record, f, indent=2)

if __name__ == "__main__":
    build_env()
