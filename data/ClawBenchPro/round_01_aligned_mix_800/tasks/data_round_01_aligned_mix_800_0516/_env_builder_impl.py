import os
import json
import random

def build_env():
    random.seed(1269) # Ensure deterministic wasteland generation

    # 1. Create directory structure
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("data/registry", exist_ok=True)
    
    # 2. Generate Volunteer Master Registry
    names = [
        "Alice Smith", "Bob Johnson", "Charlie Davis", "Elena Rodriguez", 
        "Frank White", "Grace Lee", "Henry Ford", "Isabella Swan", 
        "Jack Ryan", "Karen Page", "Liam Neeson", "Mia Wallace",
        "Noah Carter", "Olivia Pope", "Peter Parker", "Quinn Fabray",
        "Rachel Green", "Sam Winchester", "Tara Maclay", "Ursula Buffay"
    ]
    volunteers = {f"V-{100+i:03d}": name for i, name in enumerate(names)}
    
    with open("data/registry/volunteers.json", "w", encoding="utf-8") as f:
        json.dump(volunteers, f, indent=4)

    # 3. Generate Revoked IDs (Noise/Constraint)
    # Let's revoke 4 volunteers.
    revoked = ["V-103", "V-107", "V-111", "V-118"]
    with open("data/registry/revoked_ids.txt", "w", encoding="utf-8") as f:
        f.write("# REVOKED BADGES - DO NOT ACCEPT DONATIONS FROM THESE IDs\n")
        for r in revoked:
            f.write(f"{r}\n")

    # 4. Generate highly fragmented and noisy records
    event_codes = ["OPT-2023-MAIN", "TEST-DRIVE-01", "OPT-2022-OLD", "BETA-EVENT"]
    usable_conditions = [" Usable ", "GOOD condition", "USABLE", "  gOod  ", "usable frames"]
    scrap_conditions = ["Scrap", "broken glass", " SCRAP ", "totally broken", "scrap-level 2"]
    junk_conditions = ["needs review", "unknown", "pending", ""]

    all_conditions = usable_conditions + scrap_conditions + junk_conditions
    all_vids = list(volunteers.keys()) + ["V-999", "V-888"] # Add some completely fake IDs

    # Generate 300 files spread across random dates
    for i in range(1, 301):
        month = random.randint(9, 11)
        day = random.randint(1, 30)
        folder_path = f"data/records/2023/{month:02d}/{day:02d}"
        os.makedirs(folder_path, exist_ok=True)
        
        # Decide if this is a main event file or decoy
        is_main_event = random.random() > 0.4 # 60% chance of being main event
        event_code = "OPT-2023-MAIN" if is_main_event else random.choice(event_codes[1:])
        
        # Generate random donations
        donations = []
        for _ in range(random.randint(1, 15)):
            donations.append({
                "volunteer_id": random.choice(all_vids),
                "item": random.choice(["Reading Glasses", "Sunglasses", "Aviators", "Kids Frames", "Lenses"]),
                "condition": random.choice(all_conditions)
            })
            
        record = {
            "record_id": f"REC-{i:05d}",
            "event_code": event_code,
            "metadata": {"exported_by": "system", "status": "raw"},
            "donations": donations
        }
        
        # Mix in some decoy file extensions or hidden files
        file_ext = random.choice([".json", ".json", ".json", ".json.bak", ".tmp"])
        file_path = os.path.join(folder_path, f"batch_{i:04d}{file_ext}")
        
        # If it's not a standard json, maybe format it weirdly or just dump as string
        if file_ext == ".json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
        else:
            # Noise files
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n# BACKUP CORRUPTED")

if __name__ == "__main__":
    build_env()
