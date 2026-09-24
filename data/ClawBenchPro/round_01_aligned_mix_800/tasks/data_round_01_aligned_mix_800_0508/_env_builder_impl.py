import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Setup deterministic generation but simulate chaos
    random.seed(1318)
    
    base_dir = "legacy_records"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Generate Policies
    policies_dir = os.path.join(base_dir, "policies_dump")
    os.makedirs(policies_dir, exist_ok=True)
    
    policies_db = {}
    
    # Create 500 policies
    for i in range(1, 501):
        pid = f"POL-{i:05d}"
        limit = round(random.uniform(1000.0, 50000.0), 2)
        
        # Determine status
        status_roll = random.random()
        if status_roll < 0.8:
            status = "ACTIVE"
        elif status_roll < 0.9:
            status = "CANCELLED"
        else:
            status = "EXPIRED"
            
        # Active date between 2020 and 2023
        start_date = datetime(2020, 1, 1)
        active_date = start_date + timedelta(days=random.randint(0, 1000))
        date_str = active_date.strftime("%Y-%m-%d")
        
        policies_db[pid] = {
            "policy_id": pid,
            "limit": limit,
            "active_date": date_str,
            "status": status
        }

    # Scatter policies into CSVs and JSONs in subfolders
    policy_list = list(policies_db.values())
    random.shuffle(policy_list)
    
    # 1. Main CSV
    os.makedirs(os.path.join(policies_dir, "archive_csv"), exist_ok=True)
    with open(os.path.join(policies_dir, "archive_csv", "batch_1.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["policy_id", "limit", "active_date", "status"])
        writer.writeheader()
        writer.writerows(policy_list[:250])
        
    # 2. JSON fragments
    for i, p in enumerate(policy_list[250:]):
        sub_folder = os.path.join(policies_dir, f"shard_{i % 10}")
        os.makedirs(sub_folder, exist_ok=True)
        with open(os.path.join(sub_folder, f"meta_{p['policy_id']}.json"), "w", encoding="utf-8") as f:
            json.dump(p, f)
            
    # Add noise to policies
    with open(os.path.join(policies_dir, "archive_csv", "batch_old.bak"), "w") as f:
        f.write("BINARY GARBAGE\x00\x01\x02" * 100)

    # Generate Claims
    claims_dir = os.path.join(base_dir, "extracted_claims")
    
    # We will generate 1500 claims. 
    # Most are valid. Some are WITHDRAWN. Some are structurally invalid to test rules.
    for i in range(1, 1501):
        cid = f"CLM-9{i:05d}"
        
        # Pick a random policy (or rarely, a nonexistent one)
        if random.random() < 0.02:
            pid = f"POL-99999" # Nonexistent
            p_limit = 5000.0
            p_date = datetime(2022, 1, 1)
            p_status = "ACTIVE"
        else:
            pid = random.choice(list(policies_db.keys()))
            p_limit = policies_db[pid]["limit"]
            p_date = datetime.strptime(policies_db[pid]["active_date"], "%Y-%m-%d")
            p_status = policies_db[pid]["status"]
            
        # Determine claim properties
        # Amount formatting
        base_amount = round(random.uniform(500.0, p_limit * 0.9), 2)
        
        # Decide if this claim should be a forced rule violator
        is_violator = random.random() < 0.1
        violation_type = random.choice(["amount", "date", "status"]) if is_violator else None
        
        if is_violator and violation_type == "amount":
            base_amount = p_limit + round(random.uniform(100.0, 5000.0), 2)
            
        if random.random() < 0.5:
            amount_str = f"${base_amount:,.2f}" # e.g. $5,200.50
        else:
            amount_str = str(base_amount)
            
        # Date formatting
        if is_violator and violation_type == "date":
            loss_date = p_date - timedelta(days=random.randint(1, 100))
        else:
            loss_date = p_date + timedelta(days=random.randint(1, 300))
        loss_date_str = loss_date.strftime("%Y-%m-%d")
        
        # Status
        if random.random() < 0.15:
            claim_status = "WITHDRAWN"
        else:
            claim_status = "PENDING"
            
        claim_record = {
            "claim_id": cid,
            "policy_reference": pid,
            "amount": amount_str,
            "date_of_loss": loss_date_str
        }
        
        # Sometimes omit status to test default assumption
        if random.random() < 0.7:
            claim_record["claim_status"] = claim_status
            
        # Create deep nested structure
        year_folder = str(loss_date.year)
        month_folder = f"{loss_date.month:02d}"
        target_dir = os.path.join(claims_dir, year_folder, month_folder, f"batch_{i % 5}")
        os.makedirs(target_dir, exist_ok=True)
        
        # Save claim
        with open(os.path.join(target_dir, f"{cid}.json"), "w", encoding="utf-8") as f:
            json.dump(claim_record, f, indent=2)
            
        # Inject noise files alongside claims
        if i % 15 == 0:
            with open(os.path.join(target_dir, f"~{cid}.tmp"), "w") as f:
                f.write("temp lock file")
        if i % 25 == 0:
            with open(os.path.join(target_dir, f"{cid}_notes.corrupted"), "w") as f:
                f.write("system error: unable to read sector")

if __name__ == "__main__":
    build_env()
