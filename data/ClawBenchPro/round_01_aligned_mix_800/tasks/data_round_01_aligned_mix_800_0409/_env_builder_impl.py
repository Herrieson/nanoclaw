import os
import json
import csv
import random

def build_env():
    # 1. Build Trail System (Fragmentation & Decoys)
    states = ["CA", "OR", "NV", "WA"]
    difficulties = ["Easy", "Moderate", "Hard"]
    
    os.makedirs("parks_dept_data/regions", exist_ok=True)
    
    closures_data = []
    
    trail_counter = 1000
    for state in states:
        state_dir = f"parks_dept_data/regions/{state}"
        os.makedirs(state_dir, exist_ok=True)
        
        # Generate 50 decoy trails per state
        for _ in range(50):
            t_id = f"T_{trail_counter}"
            trail_counter += 1
            
            # Create mostly invalid combinations
            is_easy = random.choice([True, False])
            diff = "Easy" if is_easy else random.choice(["Moderate", "Hard"])
            length = random.uniform(0.5, 10.0)
            child_friendly = random.choice([True, False])
            
            trail = {
                "id": t_id,
                "name": f"Trail_{t_id}_{random.randint(10,99)}",
                "state": state,
                "difficulty": diff,
                "length_miles": round(length, 1),
                "child_friendly": child_friendly,
                "elevation_gain_ft": random.randint(100, 2000)
            }
            
            with open(f"{state_dir}/trail_{t_id}.json", "w", encoding="utf-8") as f:
                json.dump(trail, f, indent=2)
                
            # Randomly close some trails
            if random.random() < 0.4:
                closures_data.append({"trail_id": t_id, "status": "Closed"})
            else:
                closures_data.append({"trail_id": t_id, "status": "Open"})
                
            # If a decoy trail accidentally meets all criteria, mark it as Closed to ensure uniqueness
            if state == "CA" and diff == "Easy" and length < 3.0 and child_friendly:
                closures_data[-1]["status"] = "Closed"
                
    # Insert the ONE TRUE TRAIL
    target_id = "T_7777"
    target_trail = {
        "id": target_id,
        "name": "Little Bear Loop",
        "state": "CA",
        "difficulty": "Easy",
        "length_miles": 2.8,
        "child_friendly": True,
        "elevation_gain_ft": 150
    }
    with open(f"parks_dept_data/regions/CA/trail_{target_id}.json", "w", encoding="utf-8") as f:
        json.dump(target_trail, f, indent=2)
    closures_data.append({"trail_id": target_id, "status": "Open"})
    
    # Write closures
    random.shuffle(closures_data)
    with open("parks_dept_data/closures.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["trail_id", "status"])
        writer.writeheader()
        writer.writerows(closures_data)

    # 2. Build Gear System (Noise & Multi-hop)
    zones = ["shelf_alpha", "box_bravo", "drawer_charlie", "trunk_delta"]
    
    # Actual needed gear (distributed across latest files)
    true_needed_gear = [
        {"item": "Sleeping Bag Adult 1", "weight": 45.0, "unit": "oz", "status": "Needed"},
        {"item": "Toddler Sleeping Bag", "weight": 25.5, "unit": "oz", "status": "Needed"},
        {"item": "Water Filter", "weight": 340.0, "unit": "g", "status": "Needed"}, 
        {"item": "Camp Stove", "weight": 1.5, "unit": "lbs", "status": "Needed"},
        {"item": "First Aid Kit", "weight": 22.0, "unit": "oz", "status": "Needed"}
    ]
    
    # Decoy gear (old status, wrong files)
    decoy_gear_pool = [
        {"item": "Old Tent", "weight": 200, "unit": "oz", "status": "Packed"},
        {"item": "Heavy Boots", "weight": 3, "unit": "lbs", "status": "Lost"},
        {"item": "Lantern", "weight": 500, "unit": "g", "status": "Packed"},
        {"item": "Broken Stove", "weight": 1.2, "unit": "lbs", "status": "Needed"} # This goes into old files
    ]
    
    os.makedirs("garage_inventory/zones", exist_ok=True)
    
    needed_idx = 0
    for zone in zones:
        zone_dir = f"garage_inventory/zones/{zone}"
        os.makedirs(zone_dir, exist_ok=True)
        
        # Generate 3-5 old manifest files
        old_timestamps = [f"202310{str(i).zfill(2)}" for i in range(1, random.randint(4, 7))]
        for ts in old_timestamps:
            with open(f"{zone_dir}/manifest_{ts}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["item", "weight", "unit", "status"])
                writer.writeheader()
                for _ in range(random.randint(3, 6)):
                    writer.writerow(random.choice(decoy_gear_pool))
                    
        # Generate the LATEST manifest file
        latest_ts = "20231031"
        with open(f"{zone_dir}/manifest_{latest_ts}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["item", "weight", "unit", "status"])
            writer.writeheader()
            
            # Put some decoys (not needed) in the latest file
            for _ in range(random.randint(2, 4)):
                decoy = random.choice(decoy_gear_pool).copy()
                decoy["status"] = random.choice(["Packed", "Lost"]) # Not Needed
                writer.writerow(decoy)
                
            # Put 1-2 true needed items here
            for _ in range(random.randint(1, 2)):
                if needed_idx < len(true_needed_gear):
                    writer.writerow(true_needed_gear[needed_idx])
                    needed_idx += 1
                    
    # Guarantee all needed gear is placed in the latest files
    while needed_idx < len(true_needed_gear):
        zone_dir = f"garage_inventory/zones/{random.choice(zones)}"
        with open(f"{zone_dir}/manifest_20231031.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["item", "weight", "unit", "status"])
            writer.writerow(true_needed_gear[needed_idx])
            needed_idx += 1

if __name__ == "__main__":
    build_env()
