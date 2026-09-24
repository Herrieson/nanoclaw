import os
import json
import csv
import random
import uuid

def build_env():
    # Set a fixed seed so the environment generation is deterministic and logically verifiable
    random.seed(1425)
    
    os.makedirs('reference', exist_ok=True)
    os.makedirs('logs/weekend_dumps/scanner_alpha', exist_ok=True)
    os.makedirs('logs/weekend_dumps/scanner_beta', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)
    
    # 1. Decoy & Real Registries
    valid_registry = {
        "D001": {"name": "Oxycodone", "schedule": "CII"},
        "D002": {"name": "Amoxicillin", "schedule": "Rx"},
        "D003": {"name": "Adderall", "schedule": "CII"},
        "D004": {"name": "Ibuprofen", "schedule": "OTC"},
        "D005": {"name": "Lisinopril", "schedule": "Rx"},
        "D006": {"name": "Fentanyl", "schedule": "CII"},
        "D007": {"name": "Metformin", "schedule": "Rx"},
        "D008": {"name": "Morphine", "schedule": "CII"}
    }
    with open('reference/registry_approved_202310.json', 'w') as f:
        json.dump(valid_registry, f, indent=4)
        
    decoy_registry = valid_registry.copy()
    decoy_registry["D001"]["schedule"] = "OTC" # Fatal error if the Agent uses the decoy
    with open('reference/registry_draft_v1.json', 'w') as f:
        json.dump(decoy_registry, f, indent=4)
        
    drugs = list(valid_registry.keys())
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    
    # 2. Scanner Alpha (JSON Fragmentation & Corruptions)
    for _ in range(150):
        filename = f"logs/weekend_dumps/scanner_alpha/scan_{uuid.uuid4().hex[:8]}.json"
        
        # 20% chance of a completely malformed JSON file
        if random.random() < 0.2:
            with open(filename, 'w') as f:
                f.write('[\n  {"code": "D001", "batch": "B123"') # Truncated
            continue
            
        records = []
        for _ in range(random.randint(2, 6)):
            rec = {
                "code": random.choice(drugs),
                "batch": f"B{random.randint(100, 999)}",
                "exp": f"{random.choice(years)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "qty": random.randint(10, 100)
            }
            # 15% chance of a record missing a critical field
            if random.random() < 0.15:
                rec.pop(random.choice(["code", "batch", "exp", "qty"]))
            records.append(rec)
            
        with open(filename, 'w') as f:
            json.dump(records, f)

    # 3. Scanner Beta (CSV Fragmentation & Corruptions)
    for _ in range(150):
        filename = f"logs/weekend_dumps/scanner_beta/data_{uuid.uuid4().hex[:8]}.csv"
        
        # 20% chance of a completely malformed CSV file
        if random.random() < 0.2:
            with open(filename, 'w') as f:
                f.write('code,batch,exp,qty\nD001,B123\nERROR_DISK_FULL\n\x00\x00')
            continue
            
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["code", "batch", "exp", "qty"])
            for _ in range(random.randint(2, 6)):
                row = [
                    random.choice(drugs),
                    f"B{random.randint(100, 999)}",
                    f"{random.choice(years)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    random.randint(10, 100) # quantities are generated as ints, but will be read as strings
                ]
                # 15% chance of a record containing a blank value
                if random.random() < 0.15:
                    row[random.randint(0, 3)] = "" 
                writer.writerow(row)

if __name__ == '__main__':
    build_env()
