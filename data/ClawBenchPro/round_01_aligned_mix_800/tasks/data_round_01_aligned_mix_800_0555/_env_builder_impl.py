import os
import json
import csv
import random

def build_env():
    random.seed(1490)
    
    # 1. Build DB (customers & memberships)
    os.makedirs("db", exist_ok=True)
    
    customers = []
    memberships = []
    
    # Generate 500 customers
    first_names = ["Marcus", "Sarah", "Alice", "Chloe", "David", "John", "Jane", "Bob", "Eve", "Charlie", "Oliver", "Sophia", "Liam", "Emma", "Noah"]
    last_names = ["Johnson", "Connor", "Wonderland", "Bennett", "Smith", "Doe", "Williams", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]
    
    vips_in_logs = [
        {"name": "Marcus Johnson", "level": 4, "status": "active"},
        {"name": "Sarah Connor", "level": 5, "status": "active"},
        {"name": "Chloe Bennett", "level": 4, "status": "active"},
        {"name": "Elon Tusk", "level": 5, "status": "active"},
    ]
    fake_vips = [
        {"name": "Alice Wonderland", "level": 3, "status": "active"}, # Level too low
        {"name": "David Smith", "level": 4, "status": "expired"},    # Not active
    ]
    
    special_people = vips_in_logs + fake_vips
    
    for i in range(1, 501):
        c_id = f"C-{i:04d}"
        if i <= len(special_people):
            person = special_people[i-1]
            full_name = person["name"]
            level = person["level"]
            status = person["status"]
        else:
            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            level = random.randint(1, 5)
            status = random.choice(["active", "expired", "suspended"])
            
        customers.append({"customer_id": c_id, "full_name": full_name, "email": f"{full_name.replace(' ', '.').lower()}@example.com"})
        memberships.append({"c_id": c_id, "level": level, "status": status})
        
    # Write customers.csv
    with open("db/customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "full_name", "email"])
        writer.writeheader()
        writer.writerows(customers)
        
    # Write memberships.json
    with open("db/memberships.json", "w", encoding="utf-8") as f:
        json.dump(memberships, f, indent=2)
        
    # 2. Build Logs (Scale Simulation, Fragmentation & Noise)
    junk_owners = ["NONE", "N/A", "UNKNOWN", "NULL", " ", "", "n/a", "unknown"]
    items = ["keys", "wallet", "water bottle", "VR Headset piece", "Gold Ring", "dirty sock", "Apple Watch", "Blue Jacket", "phone", "sunglasses"]
    
    for week in range(40, 45):
        week_dir = f"logs/week_{week}"
        os.makedirs(week_dir, exist_ok=True)
        
        # 20 log files per week
        for file_idx in range(1, 21):
            log_lines = []
            for hour in range(8, 22):
                for minute in range(0, 60, 15):
                    # Normal patrol noise
                    log_lines.append(f"2023-10-XX {hour:02d}:{minute:02d}:00 INFO: Routine check completed at sector {random.randint(1, 10)}.")
                    
                    # Occasionally add LOST & FOUND
                    if random.random() < 0.05: # 5% chance
                        item = random.choice(items)
                        # Decide if junk, VIP, fake_vip, or random normal customer
                        r = random.random()
                        if r < 0.4:
                            owner = random.choice(junk_owners)
                        elif r < 0.6 and week == 42: 
                            owner = random.choice([p["name"] for p in vips_in_logs])
                        elif r < 0.7:
                            owner = random.choice([p["name"] for p in fake_vips])
                        else:
                            owner = f"{random.choice(first_names)} {random.choice(last_names)}"
                            
                        # Format specified in prompt: ... [LOST & FOUND] ITEM: <the item> | OWNER: <the owner>
                        log_lines.append(f"2023-10-XX {hour:02d}:{minute:02d}:33 WARNING: [LOST & FOUND] ITEM: {item} | OWNER: {owner}")
            
            with open(f"{week_dir}/shift_log_{file_idx}.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
