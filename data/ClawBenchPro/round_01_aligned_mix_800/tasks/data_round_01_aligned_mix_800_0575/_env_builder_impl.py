import os
import json
import csv
import random

def build_env():
    random.seed(42)
    
    # Create directories
    dirs = [
        "inventory/base",
        "transactions",
        "physical_counts",
        "reference",
        "reports"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # Generate 150 drugs
    drugs = []
    for i in range(1, 151):
        drugs.append({
            "drug_id": f"DRX_{i:04d}",
            "drug_name": f"Medication_Alpha_{i}" if i % 2 == 0 else f"Pharma_Beta_{i}"
        })
        
    # Write drug catalog
    with open("reference/drug_catalog.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["drug_id", "drug_name"])
        for d in drugs:
            writer.writerow([d["drug_id"], d["drug_name"]])
            
    # Generate Base Inventory (Start of month)
    # We create several decoy files, only one is '2023-11'
    base_counts_2023_11 = {d["drug_id"]: random.randint(500, 2000) for d in drugs}
    
    decoy_periods = ["2023-08", "2023-09", "2023-10", "2023-12_draft"]
    for idx, period in enumerate(decoy_periods):
        decoy_data = {
            "metadata": {"audit_period": period, "generated_by": "system"},
            "inventory": {d["drug_id"]: random.randint(100, 3000) for d in drugs}
        }
        with open(f"inventory/base/snapshot_rev_{idx}.json", "w") as f:
            json.dump(decoy_data, f, indent=2)
            
    # The real one
    real_data = {
        "metadata": {"audit_period": "2023-11", "generated_by": "admin", "notes": "FINAL BASELINE"},
        "inventory": base_counts_2023_11.copy()
    }
    with open("inventory/base/snapshot_rev_4_final.json", "w") as f:
        json.dump(real_data, f, indent=2)
        
    # Generate Transactions
    expected_inventory = base_counts_2023_11.copy()
    
    for day in range(1, 31):
        day_dir = f"transactions/day_{day:02d}"
        os.makedirs(day_dir, exist_ok=True)
        
        daily_tx = []
        for _ in range(random.randint(50, 150)):
            drug = random.choice(drugs)["drug_id"]
            action = random.choices(["dispense", "restock"], weights=[0.8, 0.2])[0]
            qty = random.randint(1, 50)
            status = random.choices(["completed", "failed", "cancelled"], weights=[0.7, 0.15, 0.15])[0]
            
            daily_tx.append({
                "tx_id": f"TX_{day:02d}_{random.randint(1000,9999)}",
                "drug_id": drug,
                "action": action,
                "qty": qty,
                "status": status
            })
            
            # Keep track of truth
            if status == "completed":
                if action == "dispense":
                    expected_inventory[drug] -= qty
                elif action == "restock":
                    expected_inventory[drug] += qty
                    
        # Save daily tx as JSONL to simulate logs
        with open(f"{day_dir}/sys_log.jsonl", "w") as f:
            for tx in daily_tx:
                f.write(json.dumps(tx) + "\n")
                
    # Calculate expected physical counts
    physical_inventory = expected_inventory.copy()
    
    # Inject Missing Pills (Deficits)
    missing_drugs_ids = random.sample([d["drug_id"] for d in drugs], 15)
    for drug_id in missing_drugs_ids:
        deficit = random.randint(5, 100)
        # Ensure we don't drop below 0 physically
        if physical_inventory[drug_id] > deficit:
            physical_inventory[drug_id] -= deficit
        else:
            physical_inventory[drug_id] = 0

    # Split physical inventory into 4 zones
    zones = [{"name": f"zone_{i}", "data": {d["drug_id"]: 0 for d in drugs}} for i in range(1, 5)]
    
    for drug_id, total_qty in physical_inventory.items():
        # Randomly distribute total_qty across 4 zones
        parts = [random.randint(0, 100) for _ in range(4)]
        s = sum(parts)
        if s == 0:
            zones[0]["data"][drug_id] = total_qty
            continue
            
        distributed = 0
        for i in range(3):
            portion = int((parts[i] / s) * total_qty)
            zones[i]["data"][drug_id] = portion
            distributed += portion
        zones[3]["data"][drug_id] = total_qty - distributed
        
    # Write zone files
    for zone in zones:
        with open(f"physical_counts/{zone['name']}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["location", "drug_identifier", "counted_qty"])
            for d_id, qty in zone["data"].items():
                if qty > 0: # Only write if there's actually something on the shelf
                    writer.writerow([f"Shelf_{random.randint(1,9)}", d_id, qty])

if __name__ == "__main__":
    build_env()
