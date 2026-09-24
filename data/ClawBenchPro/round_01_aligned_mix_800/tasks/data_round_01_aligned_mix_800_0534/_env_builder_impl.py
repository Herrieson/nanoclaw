import os
import json
import csv
import random
import time

def build_env():
    random.seed(42) # Ensure determinism for exact reproducibility

    os.makedirs("registry", exist_ok=True)
    os.makedirs("approvals", exist_ok=True)
    os.makedirs("field_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Generate Master Roster
    roster = {}
    for i in range(1, 151):
        v_id = f"V{i:03d}"
        name = f"Volunteer_{i:03d}"
        roster[v_id] = name

    with open("registry/roster.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Volunteer_ID", "Full_Name", "Email"])
        for v_id, name in roster.items():
            writer.writerow([v_id, name, f"{name.lower()}@university.edu"])

    # 2. Generate Scattered Approvals
    # Distribute them across random nested directories
    programs = ["Bird-Watching", "Ecology", "Admin Support", "Bake Sale", "Campus Tour"]
    statuses = ["APPROVED", "DENIED", "REVOKED", "PENDING"]
    
    base_time = int(time.time()) - 1000000
    
    for i in range(1, 151):
        v_id = f"V{i:03d}"
        # Each volunteer gets 1 to 4 status updates over time
        num_updates = random.randint(1, 4)
        for update_idx in range(num_updates):
            timestamp = base_time + random.randint(1000, 50000) * update_idx
            # The last update has a higher chance of being the targeted ones to ensure we have enough valid ones
            if update_idx == num_updates - 1 and random.random() < 0.4:
                status = "APPROVED"
                program = random.choice(["Bird-Watching", "Ecology"])
            else:
                status = random.choice(statuses)
                program = random.choice(programs)
            
            dept = random.choice(["dept_bio", "dept_ops", "dept_admin", "dept_ext"])
            sub_dir = f"approvals/{dept}/month_{random.randint(1,12):02d}"
            os.makedirs(sub_dir, exist_ok=True)
            
            file_name = f"{v_id}_slip_{timestamp}_{random.randint(1000,9999)}.json"
            with open(os.path.join(sub_dir, file_name), "w") as f:
                json.dump({
                    "volunteer_id": v_id,
                    "status": status,
                    "assigned_program": program,
                    "timestamp": timestamp,
                    "reviewer": f"Staff_{random.randint(1,20)}"
                }, f, indent=2)

    # 3. Generate Messy Field Logs
    sites = ["North_Woods", "Lake_View", "Campus_Square", "East_Trail"]
    for site in sites:
        os.makedirs(f"field_logs/{site}", exist_ok=True)
        
        # Generate 20-30 log files per site
        for log_idx in range(random.randint(20, 30)):
            file_type = random.choice(["csv_type1", "csv_type2", "json"])
            file_path = f"field_logs/{site}/log_{log_idx:03d}"
            
            records_count = random.randint(5, 15)
            
            if file_type == "csv_type1":
                # Header: Name, Duration, Task
                with open(file_path + ".csv", "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Duration", "Task"])
                    for _ in range(records_count):
                        is_rogue = random.random() < 0.1
                        name = f"Rogue_Stranger_{random.randint(1,50)}" if is_rogue else random.choice(list(roster.values()))
                        hours = _generate_messy_hours()
                        task = _generate_task()
                        writer.writerow([name, hours, task])
                        
            elif file_type == "csv_type2":
                # Header: V_ID, Hours_Logged, Activity_Type (Might include non-roster IDs)
                with open(file_path + ".csv", "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["V_ID", "Hours_Logged", "Activity_Type"])
                    for _ in range(records_count):
                        is_rogue = random.random() < 0.1
                        vid = f"V99{random.randint(1,9)}" if is_rogue else random.choice(list(roster.keys()))
                        hours = _generate_messy_hours()
                        task = _generate_task()
                        writer.writerow([vid, hours, task])
                        
            else:
                # JSON Format
                data = []
                for _ in range(records_count):
                    is_rogue = random.random() < 0.1
                    if random.random() < 0.5:
                        participant = f"Rogue_Stranger_{random.randint(1,50)}" if is_rogue else random.choice(list(roster.values()))
                    else:
                        participant = f"V99{random.randint(1,9)}" if is_rogue else random.choice(list(roster.keys()))
                    
                    data.append({
                        "participant": participant,
                        "hours": _generate_messy_hours(),
                        "event": _generate_task()
                    })
                with open(file_path + ".json", "w") as f:
                    json.dump(data, f, indent=2)

def _generate_messy_hours():
    # Introduce noise in numerical data
    choices = [
        str(random.randint(1, 8)),
        str(round(random.uniform(1, 6), 1)),
        "N/A", "three", "invalid", "", "-2.5"
    ]
    weights = [0.4, 0.4, 0.05, 0.05, 0.05, 0.025, 0.025]
    return random.choices(choices, weights=weights)[0]

def _generate_task():
    # Task descriptions must be parsed for keywords
    tasks = [
        "Morning Bird-Watching session",
        "Ecology trail cleanup",
        "Office cleaning",
        "Data entry",
        "Bake sale preparation",
        "Advanced ecology research",
        "bird-watching (rainy)",
        "Campus tour guide"
    ]
    return random.choice(tasks)

if __name__ == "__main__":
    build_env()
