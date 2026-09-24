import os
import random
import json
import csv

def build_env():
    # 🚨 Execution context: cwd is 'assets/data_round_01_aligned_mix_800_0464/'
    
    # 1. Create a deep, messy directory structure
    base_dir = "production_archive"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("final_report", exist_ok=True)
    
    sub_dirs = ["node_alpha/logs/err", "node_beta/cache/tmp", "node_gamma/recovery/dump", "system/backup/vault"]
    for d in sub_dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)

    # 2. Fragmented Mapping Data (The "Scavenger Hunt" part)
    # Split the rep-to-region mapping across different formats and locations
    map_part1 = [["rep", "region"], ["Jim", "West"], ["Pam", "East"]]
    with open(os.path.join(base_dir, "node_alpha/logs/map_fragment_A.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerows(map_part1)
    
    map_part2 = {"Dwight": "North", "Angela": "South"}
    with open(os.path.join(base_dir, "system/backup/vault/region_mapping_B.json"), "w") as f:
        json.dump(map_part2, f)
        
    with open(os.path.join(base_dir, "node_gamma/recovery/dump/README_MAP.txt"), "w") as f:
        f.write("Oscar belongs to Central region. Manual override entry.")

    # 3. Massive Noise Generation (The "Waste Land")
    reps = ["Jim", "Pam", "Dwight", "Angela", "Oscar"]
    regions = ["West", "East", "North", "South", "Central"]
    
    # Generate 500+ decoy files
    for i in range(500):
        d = os.path.join(base_dir, random.choice(sub_dirs))
        filename = f"sys_log_{random.randint(10000, 99999)}.tmp"
        with open(os.path.join(d, filename), "w") as f:
            f.write(f"HEARTBEAT {random.random()} | STATUS: OK | TIMESTAMP: {random.randint(1000,9000)}")

    # 4. Actual Sales Data (The "Truth")
    # Scattered across 4 files with heavy duplicates and noise
    valid_transactions = [
        ("TX_9901", "Jim", 4500),    # Valid
        ("TX_9902", "Pam", 850),     # Under 1000
        ("TX_9903", "Dwight", 12000), # Valid
        ("TX_9904", "Angela", 2200),  # Valid
        ("TX_9905", "Oscar", 5500),   # Valid
        ("TX_9901", "Jim", 4500),    # Duplicate
        ("TX_9906", "Pam", 3100),    # Valid
        ("TX_9907", "Dwight", 400),   # Under 1000
        ("TX_9903", "Dwight", 12000), # Duplicate
        ("TX_9908", "Oscar", 7000)    # Valid
    ]
    
    # Inject real data into specific files
    truth_files = [
        ("node_alpha/logs/err/recovery_01.dat", valid_transactions[0:3]),
        ("node_beta/cache/tmp/temp_cache_99.tmp", valid_transactions[3:6]),
        ("node_gamma/recovery/dump/dump_sector_7.dat", valid_transactions[6:8]),
        ("system/backup/vault/master_log_final.tmp", valid_transactions[8:])
    ]
    
    for path, data in truth_files:
        full_path = os.path.join(base_dir, path)
        with open(full_path, "w") as f:
            for txid, rep, amt in data:
                # Add extra formatting noise within the "real" files
                f.write(f"[DATA_STREAM] ID:{txid} | REP:{rep} | AMOUNT:{amt} | CRC_OK\n")

if __name__ == "__main__":
    build_env()
