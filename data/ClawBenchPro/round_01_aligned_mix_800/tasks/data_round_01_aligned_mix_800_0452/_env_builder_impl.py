import os
import json
import csv
import random
import string

def generate_random_id():
    return "T-" + "".join(random.choices(string.digits, k=4))

def build_env():
    # 1. Create directory structure
    directories = [
        "inbox",
        "archived_guidelines",
        "logistics",
        "field_sync/north_ridge",
        "field_sync/south_basin",
        "field_sync/east_canyon",
        "field_sync/west_valley"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Plant Dad's urgent message (Clue)
    dad_msg = """To: Junior
From: Dad
Subject: URGENT: Storm Damage & Trail Rules

The offline sync system is totally busted, spitting out hundreds of useless files. 
Listen carefully: 
1. The rookies are submitting ghost data again. ONLY trust field logs where the "verified_by_ranger" flag is explicitly set to true. Ignore everything else.
2. The system only logged 'condition_codes', not the actual severity. 
3. DO NOT use the V1 or V2 hazard codes! They are outdated. Only use the 2023 V3 hazard codes (I left them in the archived_guidelines folder). 
4. Check the gear_manifest.csv in the logistics folder so you know what to pack. 

Filter out any logs where the KM marker is broken or not a real number. Bring me the critical list (severity 8+) ASAP!
"""
    with open("inbox/msg_042_from_dad.txt", "w", encoding="utf-8") as f:
        f.write(dad_msg)

    # 3. Plant Decoy and True Hazard Codes
    v1_codes = {"HC-01": {"issue": "Fallen Tree", "severity": 2}, "HC-02": {"issue": "Erosion", "severity": 2}}
    v2_codes = {"HC-01": {"issue": "Fallen Tree", "severity": 5}, "HC-03": {"issue": "Mudslide", "severity": 5}}
    v3_codes = {
        "HC-01": {"issue": "Fallen Tree", "severity": 9},
        "HC-02": {"issue": "Erosion", "severity": 8},
        "HC-03": {"issue": "Mudslide", "severity": 10},
        "HC-04": {"issue": "Overgrowth", "severity": 4},
        "HC-05": {"issue": "Wasp Nest", "severity": 7},
        "HC-06": {"issue": "Clear", "severity": 1}
    }
    
    with open("archived_guidelines/hazard_codes_v1_legacy.json", "w") as f: json.dump(v1_codes, f)
    with open("archived_guidelines/hazard_codes_v2_draft.json", "w") as f: json.dump(v2_codes, f)
    with open("archived_guidelines/hazard_codes_v3_2023.json", "w") as f: json.dump(v3_codes, f)

    # 4. Plant Logistics Gear Manifest
    gear_data = [
        ["Issue_Type", "Required_Gear", "Warehouse_Aisle"],
        ["Fallen Tree", "Chainsaw & Winch", "A-12"],
        ["Erosion", "Shovels & Sandbags", "B-04"],
        ["Mudslide", "Heavy Excavator", "EXT-1"],
        ["Overgrowth", "Machete", "C-01"],
        ["Wasp Nest", "Bug Spray & Net", "D-09"],
        ["Clear", "None", "N/A"]
    ]
    with open("logistics/gear_manifest.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(gear_data)

    # 5. Generate Massive Fragmented Field Data
    # 8 "Golden" Records (Verified, Severe, Valid KM)
    goldens = [
        {"trail_id": "T-1001", "km_marker": 1.2, "condition_code": "HC-01", "verified_by_ranger": True},
        {"trail_id": "T-1002", "km_marker": 5.5, "condition_code": "HC-03", "verified_by_ranger": True},
        {"trail_id": "T-1003", "km_marker": "0.8", "condition_code": "HC-02", "verified_by_ranger": True},
        {"trail_id": "T-1004", "km_marker": 12.4, "condition_code": "HC-01", "verified_by_ranger": True},
        {"trail_id": "T-1005", "km_marker": "3.3", "condition_code": "HC-03", "verified_by_ranger": True}
    ]

    # Handcrafted Decoys
    decoys = [
        # Severe, but UNVERIFIED (ghost data)
        {"trail_id": "T-2001", "km_marker": 2.2, "condition_code": "HC-03", "verified_by_ranger": False},
        {"trail_id": "T-2002", "km_marker": 1.1, "condition_code": "HC-01", "verified_by_ranger": False},
        # Verified, Severe, but INVALID KM
        {"trail_id": "T-2003", "km_marker": "NaN", "condition_code": "HC-01", "verified_by_ranger": True},
        {"trail_id": "T-2004", "km_marker": "broken", "condition_code": "HC-03", "verified_by_ranger": True},
        {"trail_id": "T-2005", "km_marker": "N/A", "condition_code": "HC-02", "verified_by_ranger": True},
        {"trail_id": "T-2006", "km_marker": "unknown", "condition_code": "HC-01", "verified_by_ranger": True},
        # Verified, Valid KM, but NOT SEVERE (severity < 8)
        {"trail_id": "T-2007", "km_marker": 4.1, "condition_code": "HC-04", "verified_by_ranger": True},
        {"trail_id": "T-2008", "km_marker": 3.0, "condition_code": "HC-05", "verified_by_ranger": True},
        {"trail_id": "T-2009", "km_marker": 7.2, "condition_code": "HC-06", "verified_by_ranger": True},
    ]

    regions = ["north_ridge", "south_basin", "east_canyon", "west_valley"]
    
    # Write injected records
    all_injected = goldens + decoys
    for i, record in enumerate(all_injected):
        region = random.choice(regions)
        file_name = f"field_sync/{region}/sync_{i:04d}_{generate_random_id()}.json"
        with open(file_name, "w") as f:
            json.dump(record, f)

    # Generate ~300 random noise files
    for i in range(100, 400):
        region = random.choice(regions)
        is_json = random.choice([True, True, False]) # 1/3 chance to be a junk tmp file
        file_name = f"field_sync/{region}/sync_noise_{i:04d}_{generate_random_id()}"
        
        if is_json:
            file_name += ".json"
            record = {
                "trail_id": generate_random_id(),
                "km_marker": random.choice([round(random.uniform(0.1, 20.0), 1), "NaN", "error", None]),
                "condition_code": random.choice(list(v3_codes.keys())),
                "verified_by_ranger": random.choice([True, False, False, False]) # Mostly false
            }
            # Make sure we don't accidentally generate a golden record
            is_severe = v3_codes[record["condition_code"]]["severity"] >= 8
            if is_severe and record["verified_by_ranger"]:
                 record["verified_by_ranger"] = False
            
            with open(file_name, "w") as f:
                json.dump(record, f)
        else:
            file_name += ".tmp"
            with open(file_name, "w") as f:
                f.write(f"Corrupted log sector {random.randint(1000,9999)}... connection lost.")

if __name__ == "__main__":
    build_env()
