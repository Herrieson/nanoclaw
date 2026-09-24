import os
import json
import csv
import random
import yaml

def build_env():
    # Set seed for reproducibility
    random.seed(1557)
    
    # 1. Create directory structure
    dirs = [
        "registry/zone_north", "registry/zone_south", "registry/zone_east", "registry/zone_west",
        "planning", "checkpoints", "assets", "logs/junk"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 2. Generate Equipment Catalog (assets/equipment.yaml)
    equipment_data = {
        "categories": {
            "gardening_tools": [
                {"code": "GT-101", "desc": "Shovel"},
                {"code": "GT-102", "desc": "Rake"}
            ],
            "hydration_gear": [
                {"code": "HYD-PLAST", "desc": "Single-use Plastic Bottle", "eco_friendly": False},
                {"code": "HYD-REUSE-01", "desc": "HydroFlask 32oz", "eco_friendly": True},
                {"code": "HYD-REUSE-02", "desc": "Nalgene BPA-Free", "eco_friendly": True},
                {"code": "HYD-REUSE-03", "desc": "Metal Canteen", "eco_friendly": True}
            ],
            "apparel": [
                {"code": "APP-GLV", "desc": "Gardening Gloves"}
            ]
        }
    }
    with open("assets/equipment.yaml", "w") as f:
        yaml.dump(equipment_data, f)
        
    # 3. Generate Volunteer Data (Scattered JSONs)
    volunteers = []
    zones = ["registry/zone_north", "registry/zone_south", "registry/zone_east", "registry/zone_west"]
    
    for i in range(1, 801):
        vid = f"V-{i:04d}"
        name = f"Volunteer_{i}"
        dob = random.randint(1950, 2012)
        status = random.choice(["active", "active", "active", "withdrawn", "banned"])
        
        volunteers.append({
            "vid": vid,
            "name": name,
            "dob": dob,
            "status": status
        })
        
    # Scatter them into files (10 records per file)
    for z in zones:
        zone_vols = random.sample(volunteers, len(volunteers) // 4)
        for i in range(0, len(zone_vols), 10):
            chunk = zone_vols[i:i+10]
            with open(f"{z}/data_batch_{i}.json", "w") as f:
                json.dump({"records": chunk}, f)
                
    # 4. Generate Commitments (planning/commitments.csv)
    # Add noise: non-existent IDs
    with open("planning/commitments.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["volunteer_id", "shifts", "hours_per_shift", "notes"])
        for v in volunteers:
            shifts = random.randint(1, 5)
            hps = random.randint(2, 6)
            writer.writerow([v["vid"], shifts, hps, "confirmed"])
        # Noise
        for i in range(200):
            writer.writerow([f"V-99{i:02d}", random.randint(1,5), random.randint(2,6), "ghost_record"])

    # 5. Generate Checkpoint Logs (checkpoints/gate_day_X.log)
    # Reusable codes
    reusable_codes = ["HYD-REUSE-01", "HYD-REUSE-02", "HYD-REUSE-03"]
    bad_codes = ["HYD-PLAST", "GT-101", "GT-102", "APP-GLV"]
    
    for day in range(1, 6):
        with open(f"checkpoints/gate_day_{day}.log", "w") as f:
            f.write(f"--- SECURITY LOG DAY {day} ---\n")
            f.write("Format: [TIMESTAMP] VID | ITEMS_SCANNED\n\n")
            
            # Pick a random subset of volunteers for this day
            daily_vols = random.sample(volunteers, 300)
            for v in daily_vols:
                hour = random.randint(7, 10)
                minute = random.randint(0, 59)
                
                # Determine what they brought
                items = random.sample(bad_codes, random.randint(1, 2))
                
                # ~40% chance they brought a reusable bottle
                if random.random() < 0.4:
                    items.append(random.choice(reusable_codes))
                    
                items_str = ",".join(items)
                f.write(f"[{hour:02d}:{minute:02d}] {v['vid']} | {items_str}\n")
                
            # Add some corrupted lines as noise
            for _ in range(10):
                f.write(f"[??:??] CORRUPTED_DATA | ERROR_READING_SCANNER\n")
                
    # 6. Generate Decoy files
    with open("logs/junk/old_rules.txt", "w") as f:
        f.write("2021 Rules: Anyone over 12 can volunteer. Plastics are OK.")
    with open("planning/old_commitments_backup.csv", "w") as f:
        f.write("volunteer_id,hours\nV-0001,100\n")

if __name__ == "__main__":
    build_env()
