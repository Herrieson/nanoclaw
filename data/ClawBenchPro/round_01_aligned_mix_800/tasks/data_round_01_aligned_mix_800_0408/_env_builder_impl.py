import os
import csv
import json
import uuid
import random
from datetime import datetime, timedelta

def build_env():
    # Setup directories
    os.makedirs("records/volunteers/applicants", exist_ok=True)
    os.makedirs("records/volunteers/first_aid_certs", exist_ok=True)
    for month in range(1, 13):
        os.makedirs(f"supplies/receipts/{month:02d}", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Seed for reproducibility in noise generation
    random.seed(1674)

    # 1. Generate Volunteers Data
    # 5 Target Volunteers who meet ALL criteria
    target_volunteers = [
        {"id": "V-TARGET-001", "name": "Mike Smith"},
        {"id": "V-TARGET-002", "name": "Sarah Connor"},
        {"id": "V-TARGET-003", "name": "Ellen Ripley"},
        {"id": "V-TARGET-004", "name": "Tony Stark"},
        {"id": "V-TARGET-005", "name": "Bruce Wayne"}
    ]

    # Generate 495 decoy volunteers
    all_volunteers = target_volunteers.copy()
    for i in range(495):
        all_volunteers.append({
            "id": f"V-DECOY-{i:03d}",
            "name": f"Parent_{i:03d} Doe"
        })
    
    random.shuffle(all_volunteers)

    bg_checks_data = []
    
    for vol in all_volunteers:
        # 1.1 Write Applicant JSON
        # Some are buried in weird sub-folders just to add fragmentation noise, though we'll keep it simple flat for applicants here, but with messy names
        file_suffix = str(uuid.uuid4())[:8]
        with open(f"records/volunteers/applicants/app_{vol['id']}_{file_suffix}.json", "w") as f:
            json.dump({"applicant_id": vol['id'], "name": vol['name'], "apply_date": "2023-11-01"}, f)

        # 1.2 Generate BG Check and First Aid Cert
        if vol in target_volunteers:
            # Target: Pass, Date > 2024-05-15, Cert Active
            bg_checks_data.append({"applicant_id": vol['id'], "status": "Pass", "valid_until": "2024-05-16"})
            
            cert_content = f"""
            --- MEDICAL CERTIFICATION BOARD ---
            This document certifies that the individual holding Applicant ID: {vol['id']}
            has successfully completed the Advanced Wilderness First Aid training.
            
            Issue Date: 2023-01-10
            Notes: Excellent performance in CPR drills.
            Status: Active
            ------------------------------------
            """
            with open(f"records/volunteers/first_aid_certs/cert_{uuid.uuid4()}.txt", "w") as f:
                f.write(cert_content)
        else:
            # Decoys: Fail on various conditions
            fail_type = random.choice(["bad_bg", "expired_bg", "no_cert", "expired_cert", "wrong_status_cert"])
            
            if fail_type == "bad_bg":
                bg_checks_data.append({"applicant_id": vol['id'], "status": random.choice(["Fail", "Pending"]), "valid_until": "2025-01-01"})
            elif fail_type == "expired_bg":
                bg_checks_data.append({"applicant_id": vol['id'], "status": "Pass", "valid_until": random.choice(["2024-05-15", "2024-05-14", "2023-12-31"])})
            else:
                bg_checks_data.append({"applicant_id": vol['id'], "status": "Pass", "valid_until": "2025-05-20"})
            
            if fail_type == "expired_cert":
                cert_content = f"Applicant ID: {vol['id']}\nTraining: First Aid\nStatus: Expired\n"
                with open(f"records/volunteers/first_aid_certs/cert_{uuid.uuid4()}.txt", "w") as f:
                    f.write(cert_content)
            elif fail_type == "wrong_status_cert":
                cert_content = f"Applicant ID: {vol['id']}\nTraining: First Aid\nStatus: Revoked\n"
                with open(f"records/volunteers/first_aid_certs/cert_{uuid.uuid4()}.txt", "w") as f:
                    f.write(cert_content)
            # "no_cert" generates no file

    # Shuffle and write bg_checks.csv
    random.shuffle(bg_checks_data)
    with open("records/volunteers/bg_checks.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["applicant_id", "status", "valid_until"])
        writer.writeheader()
        writer.writerows(bg_checks_data)


    # 2. Generate Receipts Data
    # Target Receipts: 25 receipts, total cost = 540.25
    # Decoys: 300 receipts with different event_codes or statuses
    
    def generate_items(num_items):
        items = []
        for _ in range(num_items):
            cost = random.choice([5.25, 10.50, 15.00, 22.75, 8.50])
            qty = random.randint(1, 5)
            items.append({"item": f"Supply_{random.randint(1,99)}", "cost": cost, "quantity": qty})
        return items

    total_expected_cost = 0.0

    # Generate Target Receipts
    for _ in range(25):
        month = random.randint(1, 12)
        items = generate_items(random.randint(1, 4))
        receipt_cost = sum(i["cost"] * i["quantity"] for i in items)
        total_expected_cost += receipt_cost
        
        receipt_data = {
            "receipt_id": f"REC-{uuid.uuid4()}",
            "event_code": "6TH-GRADE-HIKE-24",
            "status": "Paid",
            "purchases": items,
            "timestamp": f"2024-{month:02d}-10T10:00:00Z"
        }
        with open(f"supplies/receipts/{month:02d}/{uuid.uuid4()}.json", "w") as f:
            json.dump(receipt_data, f, indent=2)

    # Generate Decoy Receipts
    for _ in range(300):
        month = random.randint(1, 12)
        items = generate_items(random.randint(1, 4))
        
        event_code = random.choice([
            "6TH-GRADE-HIKE-24", # Might have wrong status
            "8TH-GRADE-TRIP-24",
            "STAFF-RETREAT",
            "6TH-GRADE-HIKE-23"
        ])
        
        status = random.choice(["Paid", "Voided", "Pending", "Refunded"])
        
        # If it happens to randomly match target criteria, mutate it to avoid messing up the exact math
        if event_code == "6TH-GRADE-HIKE-24" and status == "Paid":
            status = "Voided" 
            
        receipt_data = {
            "receipt_id": f"REC-{uuid.uuid4()}",
            "event_code": event_code,
            "status": status,
            "purchases": items,
            "timestamp": f"2024-{month:02d}-15T14:30:00Z"
        }
        with open(f"supplies/receipts/{month:02d}/{uuid.uuid4()}.json", "w") as f:
            json.dump(receipt_data, f, indent=2)

    # Add Noise Files
    with open("supplies/receipts/04/backup_data.txt", "w") as f:
        f.write("Do not use these files for accounting. System backup only. event_code: 6TH-GRADE-HIKE-24 status: Paid cost: 9999.99 quantity: 1")

if __name__ == "__main__":
    build_env()
