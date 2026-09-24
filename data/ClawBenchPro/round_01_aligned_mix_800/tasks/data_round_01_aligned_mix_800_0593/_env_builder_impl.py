import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Directories
    os.makedirs("system_dumps/hr_exports", exist_ok=True)
    os.makedirs("system_dumps/live_sensors/2023_10", exist_ok=True)
    os.makedirs("system_dumps/old_backup_2022", exist_ok=True)
    os.makedirs("investigation", exist_ok=True)

    # 1. Generate HR Data
    departments = ["Sales", "IT", "Management", "Logistics", "Janitorial"]
    employees = {}
    
    # Target Suspects (hardcoded to ensure solvability and correct calculations)
    targets = [
        {"emp_id": "EMP_042", "name": "Marcus Vance", "dept": "IT", "clearance": True},
        {"emp_id": "EMP_099", "name": "Sarah Jenkins", "dept": "Management", "clearance": True},
        {"emp_id": "EMP_113", "name": "Tommy Cash", "dept": "Sales", "clearance": False},
        {"emp_id": "EMP_007", "name": "Victor Creed", "dept": "Janitorial", "clearance": False},
        {"emp_id": "EMP_055", "name": "Lena White", "dept": "Logistics", "clearance": False}
    ]
    
    for t in targets:
        employees[t["emp_id"]] = t

    # Generate noise employees
    first_names = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
    last_names = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies"]
    
    for i in range(1, 201):
        emp_id = f"EMP_{i:03d}"
        if emp_id not in employees:
            employees[emp_id] = {
                "emp_id": emp_id,
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "dept": random.choice(departments),
                "clearance": random.choice([True, False, False, False])
            }

    # Write HR files by department
    for dept in departments:
        dept_emps = [e for e in employees.values() if e["dept"] == dept]
        file_data = []
        for e in dept_emps:
            file_data.append({
                "identifier": e["emp_id"],
                "name": e["name"],
                "role_info": {"vault_clearance": e["clearance"], "active": True}
            })
        with open(f"system_dumps/hr_exports/{dept.lower()}_staff.json", "w") as f:
            json.dump(file_data, f, indent=2)

    # 2. Generate Logs
    rooms = ["Storefront", "Breakroom", "Loading Dock", "Restroom"]
    
    # Specific violations we want to inject
    # (day, in_hour, in_min, duration_mins, emp_id)
    violations = [
        (3, 23, 15, 45, "EMP_042"), # Marcus: 45m
        (14, 2, 10, 15, "EMP_113"), # Tommy: 15m
        (14, 4, 0, 30, "EMP_113"),  # Tommy: 30m -> Total 45m
        (22, 1, 5, 120, "EMP_007"), # Victor: 120m
        (31, 22, 50, 10, "EMP_099") # Sarah: 10m
    ]
    
    # Decoy events (Normal hours Vault entry, or off-hours wrong room)
    decoys = [
        (10, 14, 0, 60, "EMP_055", "The Vault"), # Normal hour, should be ignored
        (15, 3, 0, 15, "EMP_042", "Breakroom"),  # Off-hour, wrong room, ignore
        (20, 23, 0, 30, "EMP_113", "Storefront") # Off-hour, wrong room, ignore
    ]

    for day in range(1, 32):
        events = []
        base_date = datetime(2023, 10, day)
        
        # Generate random noise for the day (200-300 events)
        for _ in range(random.randint(100, 150)):
            # Random time
            hour = random.randint(0, 23)
            minute = random.randint(0, 50)
            duration = random.randint(1, 40)
            room = random.choice(rooms)
            emp = f"EMP_{random.randint(1, 200):03d}"
            
            enter_time = base_date.replace(hour=hour, minute=minute)
            exit_time = enter_time + timedelta(minutes=duration)
            
            events.append((enter_time, emp, room, "ENTER"))
            events.append((exit_time, emp, room, "EXIT"))
            
        # Inject violations
        for v_day, in_h, in_m, dur, emp_id in violations:
            if v_day == day:
                enter_time = base_date.replace(hour=in_h, minute=in_m)
                exit_time = enter_time + timedelta(minutes=dur)
                events.append((enter_time, emp_id, "The Vault", "ENTER"))
                events.append((exit_time, emp_id, "The Vault", "EXIT"))
                
        # Inject decoys
        for d_day, in_h, in_m, dur, emp_id, room in decoys:
            if d_day == day:
                enter_time = base_date.replace(hour=in_h, minute=in_m)
                exit_time = enter_time + timedelta(minutes=dur)
                events.append((enter_time, emp_id, room, "ENTER"))
                events.append((exit_time, emp_id, room, "EXIT"))

        # Sort events by time
        events.sort(key=lambda x: x[0])
        
        # Write 2023 log
        with open(f"system_dumps/live_sensors/2023_10/day_{day:02d}.log", "w") as f:
            for ev in events:
                time_str = ev[0].strftime("%Y-%m-%d %H:%M:%S")
                # Format: [TIMESTAMP] SENSOR_99 EVENT=CARD EMP_ID=XXX ACTION=YYY ZONE="ZZZ"
                f.write(f"[{time_str}] EVENT=CARD EMP_ID={ev[1]} ACTION={ev[3]} ZONE=\"{ev[2]}\"\n")

    # Generate Fake 2022 Logs
    for day in range(1, 5):
        with open(f"system_dumps/old_backup_2022/dump_{day:02d}.log", "w") as f:
            f.write(f"[2022-10-0{day} 08:00:00] EVENT=CARD EMP_ID=EMP_999 ACTION=ENTER ZONE=\"The Vault\"\n")

if __name__ == "__main__":
    build_env()
