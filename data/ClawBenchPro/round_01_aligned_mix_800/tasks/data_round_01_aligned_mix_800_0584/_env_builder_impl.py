import os
import json
import random

def build_env():
    # Set seed for deterministic generation
    random.seed(1656)

    # 1. Create Directories
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("sys_data", exist_ok=True)
    os.makedirs("inbox_scrapes", exist_ok=True)

    # 2. Build Volunteer Registry (Fragmentation & Multi-hop)
    volunteers = []
    approved_ids = set()
    all_registry_ids = set()
    
    first_names = ["Sarah", "Miles", "Ellen", "Kyle", "John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
    last_names = ["Connor", "Dyson", "Ripley", "Reese", "Smith", "Doe", "Vance", "Perez", "Kim", "Chen"]
    
    for i in range(1, 51):
        v_id = f"V-{i:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        clearance = random.choice(["passed", "passed", "pending", "failed", "suspended"])
        volunteers.append({
            "id": v_id,
            "name": name,
            "clearance": clearance,
            "joined_date": f"2022-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })
        all_registry_ids.add(v_id)
        if clearance == "passed":
            approved_ids.add(v_id)

    with open("sys_data/registry.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": {"version": "2.4", "last_updated": "2023-10-01"}, "users": volunteers}, f, indent=2)

    # 3. Build Scattered Logs (Scale & Noise)
    # 30 days of logs, multiple nodes per day
    for day in range(1, 31):
        dir_path = f"device_logs/2023/10/{day:02d}"
        os.makedirs(dir_path, exist_ok=True)
        
        for node in range(1, 4):
            # Generate valid text log
            log_lines = []
            num_entries = random.randint(5, 20)
            for _ in range(num_entries):
                event_type = random.choice(["[INFO] SYSTEM_BOOT", "[DEBUG] RFID_PULSE", "[ERROR] NETWORK_TIMEOUT", "[CHECK-IN]"])
                if event_type == "[CHECK-IN]":
                    # 90% chance from registry, 10% chance unregistered rogue ID
                    if random.random() < 0.9:
                        user_id = random.choice(list(all_registry_ids))
                    else:
                        user_id = f"V-{random.randint(800, 999)}"
                    
                    duration = random.choice([15, 30, 45, 60, 120, 180, 240])
                    log_lines.append(f"2023-10-{day:02d}T08:15:00 {event_type} ID:{user_id} DUR:{duration}m")
                else:
                    log_lines.append(f"2023-10-{day:02d}T08:15:00 {event_type} - NO_DATA")
            
            with open(f"{dir_path}/node_{node}.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")
                
            # Generate corrupted .bak decoy files
            with open(f"{dir_path}/node_{node}.bak", "w", encoding="utf-8") as f:
                f.write("CORRUPTED_SECTOR_0x0000\n" * 10)
                f.write(f"[CHECK-IN] ID:V-001 DUR:9999m\n") # Fake data to mislead if they read .bak

    # 4. Build Community Requests (Noise, Validation, Scale)
    items = ["Baby formula", "Diapers size 4", "Adult Winter coat", "Canned vegetables", "Asthma inhaler", "Bus passes", "School notebooks", "Toddler shoes", "Insulin syringes", "Blankets"]
    demographics = ["infant", "toddler", "adult", "senior", "general", "teen"]
    priorities = ["LOW", "NORMAL", "HIGH", "URGENT"]
    
    for req_idx in range(1, 301):
        filename = f"inbox_scrapes/req_{req_idx:04d}"
        
        # 10% chance to be a useless .tmp file
        if random.random() < 0.1:
            with open(f"{filename}.tmp", "w", encoding="utf-8") as f:
                f.write("INCOMPLETE_WEBHOOK_DUMP...")
            continue
            
        is_corrupt = random.random() < 0.05 # 5% chance of malformed JSON
        
        data = {
            "request_id": f"REQ-{req_idx}",
            "priority": random.choice(priorities),
            "demographic": random.choice(demographics),
            "request_text": f"Need {random.choice(items)} for family.",
            "timestamp": "1696150000"
        }
        
        # Guarantee at least a few valid hits
        if req_idx % 30 == 0:
            data["priority"] = "URGENT"
            data["demographic"] = random.choice(["infant", "toddler"])
            data["request_text"] = "URGENT MEDICAL/BABY SUPPLY: " + random.choice(["Formula", "Diapers", "Pediatric meds"])
            
        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            if is_corrupt:
                f.write("{ bad_json: 'missing quotes, trailing commas', }")
            else:
                json.dump(data, f, indent=2)

if __name__ == "__main__":
    build_env()
