import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(42) # Ensure deterministic environment generation
    
    # 1. Create Directories
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("workshop_notes", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("plans", exist_ok=True)

    # 2. Build Vendor Catalog (Multi-hop logic part 1)
    vendors = {
        "V_HIK_001": {"name": "Mountain Gear", "category": "Hiking"},
        "V_HIK_002": {"name": "Trailblazers", "category": "Hiking"},
        "V_CMP_001": {"name": "Campers Heaven", "category": "Camping"},
        "V_CMP_002": {"name": "Wilderness Supply", "category": "Camping"},
        "V_GRO_001": {"name": "Local Mart", "category": "Groceries"},
        "V_TOL_001": {"name": "Hardware Pro", "category": "Tools"},
        "V_MED_001": {"name": "City Pharmacy", "category": "Medical"}
    }
    with open("reference/vendor_catalog.json", "w") as f:
        json.dump(vendors, f, indent=4)

    # 3. Generate Messy Receipts
    # We will generate 100 CSV files to simulate scale and noise
    statuses = ["CLEARED", "PENDING", "REFUNDED", "DECLINED"]
    vendor_keys = list(vendors.keys())
    
    for i in range(1, 101):
        filename = f"receipts/batch_{i:03d}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["TXN_ID", "Amount", "Date", "Vendor_Code", "Status"])
            
            # Each file has 10-20 transactions
            num_txns = random.randint(10, 20)
            for j in range(num_txns):
                txn_id = f"TXN_{i:03d}_{j:03d}"
                amount = round(random.uniform(5.0, 150.0), 2)
                
                # Introduce deterministic specific transactions for the correct answer
                # Make sure we have a controlled sum.
                # Actually, let's just let the random logic with fixed seed dictate it.
                # But to make it robust, we'll just rely on the fixed seed.
                date_str = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d")
                v_code = random.choice(vendor_keys)
                status = random.choice(statuses)
                
                # Add some dirty data occasionally
                if random.random() < 0.05:
                    writer.writerow([txn_id, "ERROR", date_str, "UNKNOWN", "FAILED"])
                else:
                    writer.writerow([txn_id, f"{amount:.2f}", date_str, v_code, status])

    # 4. Generate Workshop Notes (Fragmentation & Noise)
    # We'll generate 150 markdown files over a timeline.
    locations = ["Shed", "Tarp", "Basement", "Attic"]
    wood_types = ["Oak", "Pine", "Cedar", "Maple", "Birch"]
    conditions = ["Good", "Rotted", "Termite-Damaged", "Warped"]
    
    base_date = datetime(2023, 5, 1)
    
    # Track the latest counts internally to verify (not needed for code, but good for logic)
    # We will generate logs chronologically.
    for i in range(1, 151):
        current_date = base_date + timedelta(days=i, hours=random.randint(0, 23))
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"workshop_notes/entry_{current_date.strftime('%Y%m%d_%H%M%S')}.md"
        
        is_inventory = random.choice([True, False, False]) # 1/3 chance to be inventory
        
        with open(filename, "w") as f:
            f.write("---\n")
            f.write(f"date: \"{date_str}\"\n")
            if is_inventory:
                loc = random.choice(locations)
                f.write("type: inventory\n")
                f.write(f"location: {loc}\n")
                f.write("---\n\n")
                f.write(f"Did another check of the {loc}. Can't stop worrying about winter.\n\n")
                f.write("Current counts:\n")
                
                num_items = random.randint(2, 5)
                for _ in range(num_items):
                    w_type = random.choice(wood_types)
                    count = random.randint(1, 10)
                    cond = random.choice(conditions)
                    # Format: - Pine board: 4 [Condition: Good]
                    f.write(f"- {w_type} board: {count} [Condition: {cond}]\n")
            else:
                f.write("type: journal\n")
                f.write("mood: anxious\n")
                f.write("---\n\n")
                f.write("The house is too quiet today. I keep hearing creaks.\n")
                f.write("I should check the locks again. Maybe I'll go count the wood later.\n")
                if random.random() > 0.5:
                    f.write("Thought I saw 5 Oak boards, but I was just dreaming.\n") # Decoy data

if __name__ == "__main__":
    build_env()
