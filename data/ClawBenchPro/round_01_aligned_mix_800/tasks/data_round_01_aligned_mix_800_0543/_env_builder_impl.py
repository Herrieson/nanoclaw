import os
import json
import random
import uuid

def build_env():
    # 1. Create Clearance Policy
    os.makedirs("hospital_records", exist_ok=True)
    policy = {
        "medical_constraints": {
            "elevation_gain_range_m": [200.0, 500.0],
            "max_steepness_m_per_km": 100.0
        },
        "notes": "Ensure total_gain ignores negative slopes. Steepness is the absolute max positive slope."
    }
    with open("hospital_records/clearance_policy.json", "w") as f:
        json.dump(policy, f, indent=4)

    # 2. Setup the Forestry Active List & Dumps
    os.makedirs("forestry_dept", exist_ok=True)
    os.makedirs("telemetry_dumps", exist_ok=True)

    active_trails = set()
    valid_answers = 0
    all_trail_ids = [f"trail_{str(i).zfill(3)}" for i in range(1, 301)]
    
    # Decide which trails are "active" (about 100 of them)
    active_pool = random.sample(all_trail_ids, 100)
    
    # Write active list with noise
    with open("forestry_dept/active_trails_q3.txt", "w") as f:
        f.write("=== AUTHORIZED TRAILS FOR Q3 ===\n")
        f.write("Note: Do not use trails not listed here.\n\n")
        for tid in active_pool:
            f.write(f" - {tid} (cleared by ranger operations)\n")
            active_trails.add(tid)
        f.write("\n=== END OF REPORT ===\n")

    # 3. Generate Telemetry Data
    # Target: We want exactly 8 valid answers inside the active pool.
    target_valid_trails = random.sample(active_pool, 8)
    
    for tid in all_trail_ids:
        trail_dir = os.path.join("telemetry_dumps", tid)
        os.makedirs(trail_dir, exist_ok=True)
        
        is_active = tid in active_trails
        is_target = tid in target_valid_trails
        
        # Decide trajectory parameters
        num_waypoints = random.randint(5, 12)
        base_timestamp = 1690000000 + random.randint(0, 1000000)
        
        waypoints = []
        current_distance = 0.0
        current_elevation = random.uniform(100.0, 500.0)
        
        total_gain = 0.0
        max_steep = 0.0
        
        if is_target:
            # Force valid generation: Gain 200~500, Max steepness <= 100
            target_gain = random.uniform(250, 450)
            avg_gain_per_step = target_gain / num_waypoints
            for i in range(num_waypoints):
                waypoints.append({
                    "wp_id": str(uuid.uuid4())[:8],
                    "timestamp": base_timestamp + i * 3600,
                    "distance_km": current_distance,
                    "elevation_m": current_elevation
                })
                # Move to next
                step_dist = random.uniform(1.0, 3.0)
                # ensure steepness < 100
                step_elev = random.uniform(20.0, step_dist * 80.0) # max 80 m/km
                current_distance += step_dist
                current_elevation += step_elev
        else:
            # Generate invalid trails (either active but invalid, or inactive)
            for i in range(num_waypoints):
                waypoints.append({
                    "wp_id": str(uuid.uuid4())[:8],
                    "timestamp": base_timestamp + i * 3600,
                    "distance_km": current_distance,
                    "elevation_m": current_elevation
                })
                step_dist = random.uniform(0.5, 2.0)
                # Chance to make steepness > 100 or negative drops to mess with gain
                if random.random() > 0.5:
                    step_elev = random.uniform(150.0, 300.0) # Very steep
                else:
                    step_elev = random.uniform(-100.0, 50.0) # Flat or drop
                current_distance += step_dist
                current_elevation += step_elev

        # Shuffle the waypoints so their file writing order and names are NOT chronological
        shuffled_waypoints = waypoints[:]
        random.shuffle(shuffled_waypoints)
        
        # Write to fragmented JSON files with decoy names
        for idx, wp in enumerate(shuffled_waypoints):
            # File names are letters or random hex to discourage alphabetical sorting
            fake_seq = hex(idx * 17)[2:].zfill(4)
            filename = os.path.join(trail_dir, f"fragment_{fake_seq}.json")
            
            # Add some noise to inactive trails to simulate corruption
            if not is_active and random.random() < 0.1:
                wp["distance_km"] = "CORRUPTED"
                
            with open(filename, "w") as f:
                json.dump(wp, f, indent=2)

if __name__ == "__main__":
    random.seed(42)
    build_env()
