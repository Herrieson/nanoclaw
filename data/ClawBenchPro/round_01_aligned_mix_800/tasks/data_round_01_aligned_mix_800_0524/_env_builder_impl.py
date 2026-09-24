import os
import json
import csv
import random
import uuid

def build_env():
    # Set random seed for reproducible "chaos"
    random.seed(1384)

    # 1. Create Directories
    os.makedirs("church_records/registry", exist_ok=True)
    os.makedirs("church_records/archived", exist_ok=True)
    os.makedirs("fair_management/shifts", exist_ok=True)
    os.makedirs("financials/receipts", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)

    # 2. Build Rosters & Distractors
    base_members = [
        "Alice Henderson", "Bob Jenkins", "Clara Smith", "Diane O'Connor", "Earl Thompson",
        "Fiona Gallagher", "George Miller", "Hannah Abbott", "Ian Wright", "Judy Hopps",
        "Kevin Bacon", "Laura Palmer", "Marty McFly", "Nancy Drew", "Oscar Wilde"
    ]
    
    revoked_members = ["Bob Jenkins", "Ian Wright", "Kevin Bacon"]
    
    # Noise: Old rosters
    with open("church_records/archived/2021_members.txt", "w") as f:
        f.write("\n".join(base_members + ["Old Man Jenkins", "Deceased Member A"]))
    with open("church_records/registry/2022_draft_roster.csv", "w") as f:
        f.write("Name,Status\n")
        for m in base_members:
            f.write(f"{m},Active\n")

    # True rosters
    with open("church_records/registry/2023_official_roster.txt", "w") as f:
        f.write("\n".join(base_members))
    with open("church_records/registry/2023_revoked_list.txt", "w") as f:
        f.write("\n".join(revoked_members))

    valid_roster = set(base_members) - set(revoked_members)

    # 3. Build Shifts (Scale & Noise)
    unauthorized_invaders = ["Frank Sinatra", "Granny Smith", "Hackerman", "John Doe"]
    # Bob Jenkins is revoked, so if he works, he is unauthorized.
    unauthorized_invaders.append("Bob Jenkins") 
    
    for day in range(1, 15):
        day_dir = f"fair_management/shifts/day_{day}"
        os.makedirs(day_dir, exist_ok=True)
        
        # 5 shift files per day, some .csv, some .log
        for shift_num in range(1, 6):
            ext = ".csv" if random.random() > 0.3 else ".log"
            filename = os.path.join(day_dir, f"booth_{shift_num}_shifts{ext}")
            
            with open(filename, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Name", "Role"])
                
                # 10 workers per shift file
                for hour in range(8, 18):
                    # 90% chance to pick a valid member, 10% chance for an invader
                    if random.random() > 0.1:
                        worker = random.choice(list(valid_roster))
                    else:
                        worker = random.choice(unauthorized_invaders)
                    
                    writer.writerow([f"{hour}:00", worker, "Cashier" if random.random()>0.5 else "Greeter"])
                    
        # Noise files in shift folders
        with open(os.path.join(day_dir, "weather_notes.txt"), "w") as f:
            f.write("Sunny, but very dusty. Classic Oklahoma.")

    # 4. Build Inventory (Multi-hop mapping)
    inventory = []
    pioneer_codes = set()
    for i in range(1, 51):
        code = f"ITEM_{i:03d}"
        if i <= 15:
            cat = "1800s_Pioneer"
            pioneer_codes.add(code)
            name = f"Pioneer Artifact {i}"
        elif i <= 30:
            cat = "Modern_Snacks"
            name = f"Snack {i}"
        else:
            cat = "Donation_Tier"
            name = f"Donation {i}"
            
        inventory.append({
            "item_code": code,
            "item_name": name,
            "collection_type": cat,
            "base_cost": round(random.uniform(1.0, 50.0), 2)
        })

    with open("inventory/catalog.json", "w") as f:
        json.dump(inventory, f, indent=4)

    # 5. Build Receipts (Scale, Noise & Logic)
    # Total ~1000 receipts scattered across 5 POS terminals
    for pos in range(1, 6):
        pos_dir = f"financials/receipts/pos_0{pos}"
        os.makedirs(pos_dir, exist_ok=True)
        
        for _ in range(200):
            receipt_id = str(uuid.uuid4())
            is_voided = random.random() < 0.15 # 15% chance of being a voided receipt
            
            items_bought = []
            for _ in range(random.randint(1, 5)):
                item_code = f"ITEM_{random.randint(1, 50):03d}"
                qty = random.randint(1, 4)
                unit_price = round(random.uniform(5.0, 100.0), 2)
                items_bought.append({
                    "code": item_code,
                    "qty": qty,
                    "unit_price": unit_price
                })
                
            receipt_data = {
                "transaction_id": receipt_id,
                "timestamp": f"2023-10-{random.randint(10,24)}T14:32:00Z",
                "voided": is_voided,
                "items": items_bought
            }
            
            with open(os.path.join(pos_dir, f"rcpt_{receipt_id}.json"), "w") as f:
                json.dump(receipt_data, f)
                
    # Add noise files masquerading as JSON or receipts
    with open("financials/receipts/system_error.log", "w") as f:
        f.write("Error 404: Printer not found on POS_02.")
    with open("financials/receipts/pos_01/test_print.json", "w") as f:
        # A completely malformed or irrelevant JSON
        json.dump({"test": "Printer head align", "status": "OK"}, f)

if __name__ == "__main__":
    build_env()
