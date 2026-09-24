import os
import csv
import json
import random

def build_env():
    # 🚨 Execution context: cwd is assets/data_round_01_aligned_mix_800_0481/
    os.makedirs("contracts", exist_ok=True)
    os.makedirs("archives/storage_west/logs", exist_ok=True)
    os.makedirs("archives/storage_east/temp", exist_ok=True)
    os.makedirs("archives/vault/backups", exist_ok=True)

    # 1. Create the Contract (The Truth)
    contract_data = [
        {"id": "CHEM_99", "name": "Heavy Duty Bleach", "price": 12.50},
        {"id": "WAX_01", "name": "Ultra-Gloss", "price": 30.00},
        {"id": "MOP_12", "name": "Industrial Mop", "price": 15.00},
        {"id": "SOAP_07", "name": "Bulk Hand Soap", "price": 10.00},
        {"id": "GEAR_44", "name": "Safety Goggles", "price": 5.50}
    ]
    with open("contracts/master_contract.json", "w") as f:
        json.dump(contract_data, f)

    # 2. Create Noisy Data and Fragments
    items = ["CHEM_99", "WAX_01", "MOP_12", "SOAP_07", "GEAR_44"]
    suppliers = ["CleanCorp", "PureSupply", "JanitorKing", "CleanCorp"]
    
    # Fragment A: Deeply nested, mix of suppliers, many rows
    with open("archives/storage_west/logs/active_log_alpha.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "item_id", "vendor", "qty", "rate"])
        # Targeted overcharge: CleanCorp, WAX_01 charged 35.00 (instead of 30.00)
        writer.writerow(["2023-11-01", "WAX_01", "CleanCorp", 10, 35.00]) # Overcharge 50.00
        # Noise
        for i in range(200):
            writer.writerow([f"2023-11-{i%28+1:02d}", random.choice(items), random.choice(suppliers), random.randint(1, 5), 10.00])

    # Fragment B: JSON format, hidden in backups
    log_beta = []
    # Targeted overcharge: CleanCorp, SOAP_07 charged 12.50 (instead of 10.00)
    log_beta.append({"item_id": "SOAP_07", "provider": "CleanCorp", "amount": 20, "unit_cost": 12.50}) # Overcharge 50.00
    # Noise
    for i in range(150):
        log_beta.append({"item_id": random.choice(items), "provider": "PureSupply", "amount": random.randint(1, 2), "unit_cost": 5.00})
    with open("archives/vault/backups/active_log_beta.json", "w") as f:
        json.dump(log_beta, f)

    # Fragment C: Semi-structured text fragment
    with open("archives/storage_east/temp/active_fragment_gamma.txt", "w") as f:
        f.write("LOG START\n")
        f.write("ENTRY|ITEM:CHEM_99|SUPPLIER:CleanCorp|QTY:5|PRICE:15.00\n") # Overcharge (15-12.5)*5 = 12.50
        for i in range(100):
            f.write(f"ENTRY|ITEM:{random.choice(items)}|SUPPLIER:JanitorKing|QTY:1|PRICE:1.00\n")
        f.write("LOG END")

    # 3. Stock Level Puzzle (Aggregation required)
    # Total stock needs to be < 15 for 'Low Stock'
    # WAX_01: 10 (Alpha) + 0 (Beta) + 0 (Gamma) = 10 (LOW)
    # SOAP_07: 0 (Alpha) + 20 (Beta) + 0 (Gamma) = 20 (NOT LOW)
    # CHEM_99: 0 (Alpha) + 0 (Beta) + 5 (Gamma) = 5 (LOW)
    # MOP_12 & GEAR_44 are scattered in noise but total < 15

    # Generate decoy files (The "Waste")
    for d in ["archives/storage_west/logs", "archives/vault/backups", "archives/storage_east/temp"]:
        for i in range(5):
            with open(os.path.join(d, f"old_record_{i}.csv"), "w") as f:
                f.write("garbage,data,obsolete\n1,2,3")

if __name__ == "__main__":
    build_env()
