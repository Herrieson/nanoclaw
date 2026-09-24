import os
import json
import random
import csv

def build_env():
    # 🚨 Executed in assets/data_round_01_aligned_mix_800_0461/
    root_dir = "archive"
    os.makedirs(root_dir, exist_ok=True)

    # Helper to generate random noise strings
    def get_noise():
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))

    # Zones of interest
    valid_zone = "7"
    out_zones = ["3", "9"]
    
    # 1. Create a Deep and Messy Directory Tree
    sub_paths = ["backups/daily", "logs/temp", "raw/fragments", "recovery/sector_01", "recovery/sector_02", "cache/dump"]
    for path in sub_paths:
        os.makedirs(os.path.join(root_dir, path), exist_ok=True)

    # 2. Generate THOUSANDS of Junk Files (The "Noise")
    for i in range(1200):
        folder = os.path.join(root_dir, random.choice(sub_paths))
        file_name = f"fragment_{i}_{get_noise()}.log"
        with open(os.path.join(folder, file_name), "w") as f:
            f.write(f"DUMP_DATA: {get_noise()}\nTIMESTAMP: 2018-05-12\nSTATUS: DISCARDED")

    # 3. Generate Valid Data Fragments (The "Truth")
    # We will spread these across the folders
    fragments = []
    
    # Fragment A: JSON (Zone 7 & 9)
    fragments.append({
        "path": "backups/daily/verified_manifest_A.json",
        "type": "json",
        "content": [
            {"tracking": "TRK-7001", "address": "101 Neon St", "zone": "7", "status": "Standard", "SYSTEM_VERIFIED": "TRUE"},
            {"tracking": "TRK-9005", "address": "99 Wasteland Dr", "zone": "9", "status": "Standard", "SYSTEM_VERIFIED": "TRUE"},
            {"tracking": "TRK-7775", "address": "1 Executive Plaza", "zone": "7", "status": "Standard", "SYSTEM_VERIFIED": "TRUE"} # VIP by prefix
        ]
    })

    # Fragment B: Key-Value Log (Zone 7 VIP & Zone 3)
    log_content = """# LOG START
SYSTEM_VERIFIED: TRUE
PACKAGE_ID: TRK-8812 | DEST: 55 Rusty Gate | ZONE: 7 | RANK: VIP
PACKAGE_ID: TRK-3002 | DEST: 12 Silence Rd | ZONE: 3 | RANK: Standard
# LOG END"""
    fragments.append({
        "path": "raw/fragments/recov_data_B.txt",
        "type": "raw",
        "content": log_content
    })

    # Fragment C: CSV (Mixed)
    fragments.append({
        "path": "recovery/sector_02/manifest_final.csv",
        "type": "csv",
        "content": [
            ["tracking_no", "addr", "zone_code", "priority_lvl", "verified_tag"],
            ["TRK-7009", "202 Grid Ave", "7", "Normal", "TRUE"],
            ["TRK-7110", "303 Silicon Way", "7", "Level_1", "TRUE"], # VIP by Level_1
            ["TRK-9011", "Far North 1", "9", "Standard", "TRUE"],
            ["TRK-7012", "404 Error Blvd", "7", "Priority", "TRUE"]   # VIP by Priority
        ]
    })

    # Write the fragments
    for frag in fragments:
        full_path = os.path.join(root_dir, frag["path"])
        if frag["type"] == "json":
            with open(full_path, "w") as f:
                json.dump(frag["content"], f)
        elif frag["type"] == "csv":
            with open(full_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(frag["content"])
                # Add the system tag at the end of file for CSV if it's not in rows
                # In this specific case, it's in the rows as 'verified_tag'
        else:
            with open(full_path, "w") as f:
                f.write(frag["content"])

    # 4. Create decoy with "SYSTEM_VERIFIED: FALSE"
    with open(os.path.join(root_dir, "cache/dump/decoy.json"), "w") as f:
        json.dump([{"tracking": "TRK-7999", "zone": "7", "SYSTEM_VERIFIED": "FALSE"}], f)

if __name__ == "__main__":
    build_env()
