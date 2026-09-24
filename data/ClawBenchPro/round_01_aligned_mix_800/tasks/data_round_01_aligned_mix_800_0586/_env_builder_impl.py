import os
import json
import csv
import random

def build_env():
    random.seed(1643) # Ensure deterministic generation

    # 1. Create main directories
    os.makedirs("signups_dump", exist_ok=True)
    os.makedirs("compliance_audits", exist_ok=True)
    
    # 2. Generate Master Roster
    roster = {}
    first_names = ["John", "Alice", "Bob", "Charlie", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", 
                   "Judy", "Karl", "Linda", "Mike", "Nancy", "Oscar", "Peggy", "Quinn", "Romeo", "Sarah"]
    last_names = ["Smith", "Doe", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
    
    all_names = list(set([f"{f} {l}" for f in first_names for l in last_names]))
    random.shuffle(all_names)
    
    for i, name in enumerate(all_names):
        worker_id = f"W-{1000 + i}"
        roster[worker_id] = name
        
    with open("master_roster.json", "w") as f:
        json.dump(roster, f, indent=2)

    # 3. Generate Compliance Audits (Noise + Real Clues)
    banned_ids = random.sample(list(roster.keys()), 15) # 15 banned workers
    
    for month in range(1, 13):
        os.makedirs(f"compliance_audits/2023_{month:02d}", exist_ok=True)
        for log_num in range(5):
            filepath = f"compliance_audits/2023_{month:02d}/audit_{log_num}.log"
            content = "AUDIT START\n"
            # Random noise
            for _ in range(random.randint(5, 15)):
                content += f"INFO: Routine check passed for Sector {random.randint(1,9)}.\n"
            
            # Inject critical violation or minor violation
            if random.random() < 0.3:
                bad_id = random.choice(banned_ids)
                content += f"[CRITICAL_VIOLATION] WorkerID: {bad_id} - Safety gear missing.\n"
            elif random.random() < 0.3:
                good_id = random.choice(list(roster.keys()))
                content += f"[MINOR_VIOLATION] WorkerID: {good_id} - Late to briefing.\n"
                
            content += "AUDIT END\n"
            with open(filepath, "w") as f:
                f.write(content)

    # 4. Generate Signups Dump (Massive scale, fragmentation, noise)
    equipments = ["leather gloves", "hammer", "pickup truck", "small backhoe", "safety glasses", 
                  "heavy Truck", "Backhoe rented", "nothing", "shovel", "water cooler"]
    statuses = ["active", "active", "active", "withdrawn", "cancelled"]
    
    for region in ["north", "south", "east", "west"]:
        for week in range(1, 5):
            dir_path = f"signups_dump/{region}/week_{week}"
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate JSON valid files
            for j_idx in range(3):
                records = []
                for _ in range(random.randint(10, 25)):
                    records.append({
                        "name": random.choice(all_names),
                        "hours": random.randint(2, 10),
                        "equipment": random.choice(equipments),
                        "status": random.choice(statuses)
                    })
                with open(f"{dir_path}/batch_{j_idx}.json", "w") as f:
                    json.dump(records, f)
            
            # Generate CSV valid files (pipe delimited)
            for c_idx in range(3):
                with open(f"{dir_path}/export_{c_idx}.csv", "w", newline='') as f:
                    writer = csv.writer(f, delimiter='|')
                    writer.writerow(["name", "hours", "equipment", "status"])
                    for _ in range(random.randint(10, 25)):
                        writer.writerow([
                            random.choice(all_names),
                            random.randint(2, 10),
                            random.choice(equipments),
                            random.choice(statuses)
                        ])
            
            # Generate NOISE files
            for n_idx in range(4):
                with open(f"{dir_path}/temp_cache_{n_idx}.bak", "w") as f:
                    f.write("01010100 01100101 01110011 01110100" * random.randint(10, 50))
                with open(f"{dir_path}/readme_{n_idx}.tmp", "w") as f:
                    f.write("This folder contains backup dumps. Do not delete without admin approval.")

if __name__ == "__main__":
    build_env()
