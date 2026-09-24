import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Set seed for deterministic output
    random.seed(1081)

    os.makedirs("compliance", exist_ok=True)
    os.makedirs("inventory_reports", exist_ok=True)
    
    # 1. Generate compliance codes
    codes = {
        "ORG-77A": "Certified Organic",
        "ORG-77B": "Certified Organic (Fair Trade)", # We only want exact "Certified Organic", let's assume prompt meant the exact mapped string "Certified Organic"
        "PND-01": "Pending",
        "REJ-XX": "Rejected",
        "ORG-99": "Certified Organic"
    }
    with open("compliance/certification_codes.json", "w") as f:
        json.dump(codes, f, indent=4)

    # 2. Generate inspector registry
    inspectors = [
        ("INSP-001", "Active"),
        ("INSP-002", "Terminated"),
        ("INSP-003", "Active"),
        ("INSP-004", "On Leave"),
        ("INSP-005", "Active")
    ]
    with open("compliance/inspector_registry.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Inspector_ID", "Status", "Last_Training_Date"])
        for ins in inspectors:
            writer.writerow([ins[0], ins[1], "2023-01-15"])

    # 3. Generate unit conversions sticky note
    with open("compliance/unit_conversions.txt", "w") as f:
        f.write("Mai's Sticky Note - DO NOT TRASH\n")
        f.write("Warehouse goons are using metric again.\n")
        f.write("Remember:\n")
        f.write("1 kg = 2.2 lbs\n")
        f.write("1 oz = 0.0625 lbs\n")
        f.write("If they forget the unit, it's lbs.\n")

    # 4. Generate hundreds of fragmented logs
    ingredients = ["Shea Butter", "Lavender Oil", "Coconut Oil", "Lye", "Rose Water", "Vitamin E", "Oatmeal"]
    units = ["lbs", "kg", "oz", ""]
    
    start_date = datetime(2023, 1, 1)
    
    for i in range(300):
        current_date = start_date + timedelta(days=i)
        date_path = os.path.join("archives", "dock_logs", str(current_date.year), f"{current_date.month:02d}", f"{current_date.day:02d}")
        os.makedirs(date_path, exist_ok=True)
        
        # Decide format for the log
        fmt = random.choice(["json", "csv", "txt"])
        file_path = os.path.join(date_path, f"receipt_batch_{i}.{fmt}")
        
        # Randomly insert trash files
        if random.random() < 0.05:
            with open(os.path.join(date_path, f"catering_{i}.txt"), "w") as f:
                f.write("Bat Mitzvah catering:\n- 50 Kosher meals\n- 20 Vegetarian\nNeeds more napkins.")
            continue

        num_entries = random.randint(3, 15)
        batch_data = []
        for _ in range(num_entries):
            ing = random.choice(ingredients)
            cert = random.choice(list(codes.keys()))
            ins = random.choice([x[0] for x in inspectors] + ["INSP-999"])
            weight_val = round(random.uniform(10.0, 500.0), 2)
            unit = random.choice(units)
            weight_str = f"{weight_val} {unit}".strip()
            
            batch_data.append({
                "item": ing,
                "cert_code": cert,
                "inspector": ins,
                "weight": weight_str
            })

        if fmt == "json":
            # Sometimes nested to add noise
            wrapper = {"metadata": {"system": "SAP", "version": "v2"}, "payload": {"items": batch_data}}
            with open(file_path, "w") as f:
                json.dump(wrapper, f)
        
        elif fmt == "csv":
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                # Shuffle headers slightly to prevent hardcoded column indices
                headers = ["ItemName", "Inspector", "Weight_Value", "Code"]
                writer.writerow(headers)
                for row in batch_data:
                    writer.writerow([row["item"], row["inspector"], row["weight"], row["cert_code"]])
                    
        elif fmt == "txt":
            with open(file_path, "w") as f:
                f.write(f"--- LOG ENTRY {i} ---\n")
                for row in batch_data:
                    f.write(f"[{row['inspector']}] Received {row['item']} - Weight: {row['weight']} (Status: {row['cert_code']})\n")

if __name__ == "__main__":
    build_env()
