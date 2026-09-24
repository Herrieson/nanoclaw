import os
import csv
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 🚨 Base directory is already assets/data_round_01_aligned_mix_800_0474/
    os.makedirs("legacy_configs", exist_ok=True)
    os.makedirs("archived_claims", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)

    # 1. Create fragmented policy whitelist clues
    # Only the latest timestamp for each policy is valid
    policies = [
        ("POL-882", 5000, "2023-01-01"),
        ("POL-882", 7500, "2023-10-15"), # Latest
        ("POL-102", 12000, "2023-05-20"), # Latest
        ("POL-443", 3000, "2022-12-01"),
        ("POL-443", 4500, "2023-11-02"), # Latest
        ("POL-991", 25000, "2023-08-14"), # Latest
    ]
    
    # Scatter policy fragments in semi-structured logs
    for i, (p_id, limit, ts) in enumerate(policies):
        sub_dir = f"legacy_configs/node_{i%3}"
        os.makedirs(sub_dir, exist_ok=True)
        with open(os.path.join(sub_dir, f"patch_{i}.log"), "w") as f:
            f.write(f"TIMESTAMP: {ts} | ACTION: UPDATE_LIMIT | TARGET: {p_id} | VAL: {limit}")

    # 2. Create massive scale claims (hundreds of files)
    valid_p_ids = {"POL-882": 7500, "POL-102": 12000, "POL-443": 4500, "POL-991": 25000}
    total_valid_sum = 0
    
    for i in range(150):
        # Noise folder structure
        depth = random.randint(1, 3)
        path = "archived_claims"
        for d in range(depth):
            path = os.path.join(path, f"sector_{random.randint(1, 5)}")
        os.makedirs(path, exist_ok=True)

        is_noise = random.choice([True, False, False]) # 1/3 chance of being noise
        suffix = random.choice(["_bak", "_deprecated", "_temp", ""]) if is_noise else ""
        ext = random.choice(["csv", "json", "txt"])
        filename = f"batch_{i}{suffix}.{ext}"
        
        # Decide if this record is valid, over-limit, or invalid ID
        type_roll = random.random()
        p_id = random.choice(list(valid_p_ids.keys()) + ["INV-999", "ERR-000"])
        
        if p_id in valid_p_ids:
            limit = valid_p_ids[p_id]
            if type_roll < 0.6: # Valid
                amount = random.randint(100, limit)
                if not is_noise: total_valid_sum += amount
            else: # Over-limit
                amount = limit + random.randint(100, 2000)
        else: # Invalid ID
            amount = random.randint(500, 5000)

        # Write data in different formats
        full_path = os.path.join(path, filename)
        record = {"Claim_ID": f"C-{i:04d}", "Policy_ID": p_id, "Claim_Amount": amount}
        
        if ext == "csv":
            with open(full_path, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=record.keys())
                writer.writeheader()
                writer.writerow(record)
        elif ext == "json":
            with open(full_path, "w") as f:
                json.dump(record, f)
        else: # txt/log format
            with open(full_path, "w") as f:
                f.write(f"ID={record['Claim_ID']}, POLICY={record['Policy_ID']}, AMT={record['Claim_Amount']}")

    # Verification value (Hidden from Agent)
    # The sum only counts non-noise files where ID is valid and AMT <= Limit.

if __name__ == "__main__":
    build_env()
