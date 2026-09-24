import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(1993) # Ensure deterministic environment generation
    
    # 1. Create Directories
    directories = [
        "compliance",
        "accounting",
        "ready_for_monday" # Create it or let agent create it? Prompt says "Create a folder", but having it doesn't hurt, we'll let agent create it to follow prompt literally, so we won't pre-create it.
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Build Multi-hop Reference: Safety Matrix
    safety_codes = {}
    for i in range(1, 151):
        code = f"HZ-{i:03d}"
        # Only a small percentage are Severity 4 or 5
        severity = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 7, 3], k=1)[0]
        safety_codes[code] = severity
    
    with open("compliance/safety_matrix.json", "w", encoding="utf-8") as f:
        json.dump(safety_codes, f, indent=2)

    # 3. Build Multi-hop Reference: Vendor Categories
    categories = ["Construction", "Art", "Personal", "Office", "Groceries", "Auto"]
    vendors = []
    for i in range(1, 201):
        vid = f"V-{i:03d}"
        cat = random.choice(categories)
        vendors.append([vid, cat])
    
    with open("accounting/vendor_categories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Vendor_ID", "Category"])
        writer.writerows(vendors)

    # 4. Generate Chaotic Site Records (Scale & Noise)
    start_date = datetime(2023, 1, 1)
    for i in range(400):
        current_date = start_date + timedelta(days=random.randint(0, 300))
        date_path = f"sync_dump/site_records/{current_date.year}/{current_date.month:02d}/{current_date.day:02d}"
        os.makedirs(date_path, exist_ok=True)
        
        inspector = random.choice(["Marcus", "Dave", "Sarah", "Auto-Sys"])
        status = random.choice(["Finalized", "Draft", "Archived", "Pending Review"])
        incident_code = random.choice(list(safety_codes.keys()))
        
        # Give valid ones a distinct description to make output clear
        is_valid = (inspector == "Marcus" and status == "Finalized" and safety_codes[incident_code] >= 4)
        desc = f"Critical hazard detected involving {incident_code} at sector {random.randint(1,9)}." if is_valid else f"Routine observation or minor issue regarding {incident_code}."
        
        log_content = f"""---
Report_ID: R-{random.randint(1000, 9999)}
Date: {current_date.strftime('%Y-%m-%d')}
Inspector: {inspector}
Status: {status}
---
Notes: Daily site walkthrough completed.
Incident_Code: {incident_code}
Incident_Desc: {desc}
"""
        with open(f"{date_path}/log_{i:04d}.txt", "w", encoding="utf-8") as f:
            f.write(log_content)

    # 5. Generate Chaotic Financial JSON Fragments (Scale & Noise)
    for i in range(600):
        # Scatter them in random subdirectories
        dir_name = f"sync_dump/financials/batch_{random.randint(1, 20):02d}"
        os.makedirs(dir_name, exist_ok=True)
        
        card = random.choice(["4921", "1111", "8822", "4921", "0000"]) # 4921 is the target
        status = random.choice(["POSTED", "PENDING", "DECLINED", "POSTED"]) # POSTED is the target
        vid = random.choice(vendors)[0]
        amount = float(random.randint(5, 500)) + random.choice([0.0, 0.25, 0.50, 0.75])
        
        txn = {
            "txn_id": f"TXN-{random.randint(10000, 99999)}",
            "vendor_id": vid,
            "amount": amount,
            "card_last4": card,
            "status": status,
            "timestamp": (start_date + timedelta(days=random.randint(0, 300))).isoformat()
        }
        
        # Add random noise fields
        if random.random() > 0.5:
            txn["geo_location"] = "Site_A"
        
        with open(f"{dir_name}/receipt_{i:04d}.json", "w", encoding="utf-8") as f:
            json.dump(txn, f, indent=2)

if __name__ == "__main__":
    build_env()
