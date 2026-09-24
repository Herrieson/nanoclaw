import os
import json
import csv
import random

def build_env():
    # Set fixed seed for deterministic wasteland generation
    random.seed(1449)
    
    # Core directories
    apps_dir = os.path.join("data_lake", "applications")
    profiles_dir = os.path.join("data_lake", "profiles")
    ref_dir = "reference"
    obsolete_ref_dir = os.path.join("reference", "obsolete_rules")
    
    for d in [apps_dir, profiles_dir, ref_dir, obsolete_ref_dir]:
        os.makedirs(d, exist_ok=True)

    # 1. Build Activity Matrix (The Truth)
    matrix_path = os.path.join(ref_dir, "activity_matrix.csv")
    activities = []
    classes = ['A', 'B', 'C', 'D']
    
    with open(matrix_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Activity_Code", "Activity_Name", "Risk_Class"])
        for i in range(1, 151):
            code = f"ACT-{i:03d}"
            # Heavily skew towards A and B, make C and D rarer
            risk_class = random.choices(classes, weights=[40, 40, 10, 10], k=1)[0]
            name = f"Hobby_Type_{i}"
            writer.writerow([code, name, risk_class])
            activities.append((code, risk_class))
            
    # Add explicit easter eggs for the prompt's legacy mention
    with open(matrix_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ACT-997", "Skydiving", "D"])
        writer.writerow(["ACT-998", "Rock Climbing", "C"])
        writer.writerow(["ACT-999", "Scuba Diving", "C"])
        activities.extend([("ACT-997", "D"), ("ACT-998", "C"), ("ACT-999", "C")])

    # 1b. Build Obsolete Decoy Matrix (The Noise)
    decoy_matrix_path = os.path.join(obsolete_ref_dir, "activity_matrix_2018.csv")
    with open(decoy_matrix_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Activity_Code", "Activity_Name", "Risk_Class"])
        for i in range(1, 151):
            code = f"ACT-{i:03d}"
            # Opposite logic to mislead lazy agents
            writer.writerow([code, f"Hobby_Type_{i}", "A"]) 

    # 2. Build Profiles
    # Generate 500 valid profiles
    valid_profile_refs = []
    for i in range(1, 501):
        prof_ref = f"PROF-{i:04d}"
        valid_profile_refs.append(prof_ref)
        num_children = random.choices([0, 1, 2, 3, 4, 5], weights=[50, 20, 15, 10, 4, 1])[0]
        # Assign 1 to 4 random activities
        client_acts = random.sample([a[0] for a in activities], k=random.randint(1, 4))
        
        prof_data = {
            "profile_ref": prof_ref,
            "personal_info": {
                "age": random.randint(22, 65),
                "children": num_children
            },
            "activity_codes": client_acts
        }
        with open(os.path.join(profiles_dir, f"{prof_ref}.json"), 'w') as f:
            json.dump(prof_data, f, indent=2)

    # 3. Build Applications (The Fragmentation & Scale)
    # Total apps: 1200
    statuses = ["PENDING", "REJECTED", "ARCHIVED", "DRAFT"]
    
    # Track used profiles to avoid duplicates in PENDING (to keep counting simple)
    available_profiles = valid_profile_refs.copy()
    random.shuffle(available_profiles)
    
    for i in range(1, 1201):
        client_id = f"CID-{i:05d}"
        file_name = f"APP_req_{i:05d}.json"
        
        # Decide if this is a valid JSON or corrupted noise (10% chance)
        if random.random() < 0.1:
            with open(os.path.join(apps_dir, file_name), 'w') as f:
                f.write(f'{{\n  "client_id": "{client_id}",\n  "approval_status": "PENDING",\n  "prof') # Cut off abruptly
            continue
            
        # Determine status
        status = random.choices(statuses, weights=[20, 30, 40, 10], k=1)[0]
        
        if status == "PENDING" and available_profiles:
            prof_ref = available_profiles.pop()
        else:
            # For non-pending, give them fake profile refs that don't exist
            # This punishes agents that don't filter by status first
            prof_ref = f"GHOST-PROF-{random.randint(1000, 9999)}"
            
        app_data = {
            "application_id": f"APP-{i:05d}",
            "client_id": client_id,
            "approval_status": status,
            "profile_ref": prof_ref,
            "system_meta": "migrated_v2"
        }
        
        with open(os.path.join(apps_dir, file_name), 'w') as f:
            json.dump(app_data, f)
            
    # Add pure junk files
    with open(os.path.join(apps_dir, ".DS_Store"), 'w') as f:
        f.write(r"Bud1\u0000\u0000\u0000\u0008\u0000\u0000\u0000")
    with open(os.path.join(apps_dir, "migration_log.txt"), 'w') as f:
        f.write("ERROR 502: Bad gateway during batch 44.\nWARN: Some JSON files truncated.")

if __name__ == "__main__":
    build_env()
