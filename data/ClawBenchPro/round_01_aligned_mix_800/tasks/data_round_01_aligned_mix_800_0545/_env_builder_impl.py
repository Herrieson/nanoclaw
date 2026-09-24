import os
import json
import csv
import random

def build_env():
    # Set a fixed seed for reproducible "random" generation
    random.seed(42)
    
    base_dir = 'campaign_mess'
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create IT Memos (Clue for Project ID)
    os.makedirs(os.path.join(base_dir, 'IT_memos'), exist_ok=True)
    with open(os.path.join(base_dir, 'IT_memos', 'memo_2022_deprecated.txt'), 'w') as f:
        f.write("DEPRECATED: Old codes\nPark Cleanup: PC-01\nFood Drive: FD-01\n")
    with open(os.path.join(base_dir, 'IT_memos', 'memo_2023_sys_upgrade.txt'), 'w') as f:
        f.write("URGENT: SYSTEM UPGRADE NOTICE\n\nAll initiatives have been migrated to the new AlphaNumeric Hash System.\n")
        f.write("Please use the following Project IDs for all records moving forward:\n")
        f.write("- Food Drive: PRJ-FD-992\n")
        f.write("- Voter Registration: PRJ-VR-105\n")
        f.write("- Park Cleanup: PRJ-CP-044\n")
        f.write("- Save The Whales: PRJ-SW-888\n")

    # 2. Generate Corporate Registry
    os.makedirs(os.path.join(base_dir, 'registry'), exist_ok=True)
    companies = []
    # Generate 200 random companies
    for i in range(1, 201):
        companies.append({
            "corp_id": f"CID-{1000 + i}",
            "business_name": f"Enterprise_{i} LLC"
        })
    
    # Insert specific targets to act as our "Flaky Businesses" later
    target_corps = [
        {"corp_id": "CID-9001", "business_name": "MegaCorp Oil"},
        {"corp_id": "CID-9002", "business_name": "Global Retailers LLC"},
        {"corp_id": "CID-9003", "business_name": "Tech Bros Inc"},
    ]
    companies.extend(target_corps)
    random.shuffle(companies)
    
    with open(os.path.join(base_dir, 'registry', 'corp_registry_master.json'), 'w') as f:
        json.dump(companies, f, indent=2)

    # 3. Generate Corporate Pledges (Fragmented CSVs with noise)
    pledges_dir = os.path.join(base_dir, 'pledges')
    os.makedirs(pledges_dir, exist_ok=True)
    
    projects = ["PRJ-FD-992", "PRJ-VR-105", "PRJ-CP-044", "PRJ-SW-888"]
    statuses = ["PAID", "PENDING", "FAILED"]
    
    for quarter in ["Q1", "Q2", "Q3", "Q4"]:
        q_dir = os.path.join(pledges_dir, quarter)
        os.makedirs(q_dir, exist_ok=True)
        for batch in range(1, 6):
            batch_data = []
            # 50 rows per batch
            for _ in range(50):
                batch_data.append({
                    "pledge_id": f"PLG-{random.randint(10000, 99999)}",
                    "corp_id": random.choice(companies)["corp_id"],
                    "project_id": random.choice(projects),
                    "amount": random.randint(100, 5000),
                    "status": random.choice(statuses)
                })
            
            # Injecting truth targets in Q3 and Q4
            if quarter == "Q3" and batch == 1:
                batch_data.append({"pledge_id": "PLG-TRUTH1", "corp_id": "CID-9001", "project_id": "PRJ-CP-044", "amount": 5000, "status": "PENDING"})
            if quarter == "Q4" and batch == 2:
                batch_data.append({"pledge_id": "PLG-TRUTH2", "corp_id": "CID-9002", "project_id": "PRJ-CP-044", "amount": 2000, "status": "PENDING"})
            if quarter == "Q2" and batch == 5:
                batch_data.append({"pledge_id": "PLG-TRUTH3", "corp_id": "CID-9003", "project_id": "PRJ-CP-044", "amount": 10000, "status": "PENDING"})
            
            # Noise: Same companies but paid, or different projects but pending
            if quarter == "Q1" and batch == 3:
                batch_data.append({"pledge_id": "PLG-NOISE1", "corp_id": "CID-9001", "project_id": "PRJ-CP-044", "amount": 500, "status": "PAID"})
                batch_data.append({"pledge_id": "PLG-NOISE2", "corp_id": "CID-9002", "project_id": "PRJ-FD-992", "amount": 2000, "status": "PENDING"})
                
            random.shuffle(batch_data)
            with open(os.path.join(q_dir, f'batch_{batch:03d}.csv'), 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["pledge_id", "corp_id", "project_id", "amount", "status"])
                writer.writeheader()
                writer.writerows(batch_data)

    # 4. Generate Volunteer Timesheets (Massively fragmented JSONs)
    timesheets_dir = os.path.join(base_dir, 'timesheets')
    os.makedirs(timesheets_dir, exist_ok=True)
    
    names = ["Sarah", "John", "Maria", "David", "Alex", "Priya", "Taylor", "Jordan"]
    ts_statuses = ["APPROVED", "DRAFT", "REJECTED"]
    
    total_truth_minutes = 0
    
    for week in range(1, 13):
        week_dir = os.path.join(timesheets_dir, f'week_{week:02d}')
        os.makedirs(week_dir, exist_ok=True)
        
        # 40 timesheets per week
        for ts_idx in range(40):
            project = random.choice(projects)
            status = random.choice(ts_statuses)
            minutes = random.randint(15, 240)
            
            # Keep track of the exact truth data we generate
            if project == "PRJ-CP-044" and status == "APPROVED":
                total_truth_minutes += minutes
                
            ts_data = {
                "ts_id": f"TS-{week}-{ts_idx}",
                "volunteer": random.choice(names),
                "project_id": project,
                "minutes_logged": minutes,
                "approval_status": status,
                "notes": "Good work!" if status == "APPROVED" else "Forgot to clock out"
            }
            
            with open(os.path.join(week_dir, f'log_{ts_idx:03d}.json'), 'w') as f:
                json.dump(ts_data, f, indent=2)

    # 5. Add a distractor directory
    os.makedirs(os.path.join(base_dir, 'old_backups'), exist_ok=True)
    with open(os.path.join(base_dir, 'old_backups', 'v1_data.json'), 'w') as f:
        json.dump({"warning": "Do not use this data, it is deprecated."}, f)

if __name__ == "__main__":
    build_env()
