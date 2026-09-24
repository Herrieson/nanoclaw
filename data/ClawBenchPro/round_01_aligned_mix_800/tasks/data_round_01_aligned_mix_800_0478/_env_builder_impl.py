import os
import csv
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Fix seed for determinism in generation
    random.seed(42)

    # 1. Create directories
    base_dirs = [
        "inventory",
        "materials_catalog",
        "reference/active_codes",
        "reference/deprecated",
        "deliverables"
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Generate Materials Catalog (Multi-hop mapping DB)
    materials = []
    # Wood materials
    woods = ["Oak", "Maple", "Cedar", "Mahogany", "Ebony", "Pine", "Birch", "Teak", "Walnut", "Rosewood"]
    for i, w in enumerate(woods):
        materials.append({"Material_ID": f"W-{100+i}", "Name": w, "Category": "Wood"})
    
    # Noise materials
    noises = ["Cement", "Steel", "Nails", "Paint", "Glass", "Copper", "Aluminum", "Brick", "Tile", "Plastic"]
    for i, n in enumerate(noises):
        materials.append({"Material_ID": f"N-{200+i}", "Name": n, "Category": random.choice(["Basic", "Metal", "Consumable", "Misc"])})
    
    # Shuffle and split into fragmented CSVs in materials_catalog
    random.shuffle(materials)
    chunks = [materials[i:i + 4] for i in range(0, len(materials), 4)]
    for idx, chunk in enumerate(chunks):
        with open(f"materials_catalog/catalog_fragment_{idx}.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Material_ID", "Name", "Category", "Supplier"])
            writer.writeheader()
            for row in chunk:
                # Add a dummy column 'Supplier' as noise
                row["Supplier"] = f"Corp_{random.randint(10,99)}"
                writer.writerow(row)

    # 3. Generate Reference Codes (Active and Deprecated)
    active_mapping = {
        "Oak": "DQ01", "Maple": "UL02", "Cedar": "MH03", 
        "Mahogany": "OP04", "Ebony": "HD05", "Teak": "FW06", "Walnut": "GR07"
    }
    # Deprecated mapping (noise/decoys)
    deprecated_mapping = [
        {"material": "Pine", "code": "DQ01"}, # Intentional overlap
        {"material": "Oak", "code": "OLD_02"},
        {"material": "Birch", "code": "XX99"}
    ]
    
    # Write deprecated
    with open("reference/deprecated/old_mapping_v1.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material", "code"])
        for d in deprecated_mapping:
            writer.writerow([d["material"], d["code"]])

    # Write active codes into fragmented JSONs
    items = list(active_mapping.items())
    random.shuffle(items)
    for i in range(0, len(items), 2):
        fragment = {k: v for k, v in items[i:i+2]}
        with open(f"reference/active_codes/code_frag_{i//2}.json", "w", encoding="utf-8") as f:
            json.dump(fragment, f, indent=2)

    # 4. Generate highly fragmented and noisy Inventory Logs
    start_date = datetime(2023, 1, 1)
    tx_counter = 1
    
    # Generate ~300 files
    for day_offset in range(30):
        current_date = start_date + timedelta(days=day_offset)
        dir_path = f"inventory/{current_date.year}/{current_date.month:02d}/{current_date.day:02d}"
        os.makedirs(dir_path, exist_ok=True)
        
        # 10 files per day
        for file_idx in range(10):
            is_approved = random.choice([True, False, False]) # 1/3 chance to be approved
            file_ext = random.choice([".log", ".tmp", ".txt", ".bak"])
            filename = f"batch_{file_idx}{file_ext}"
            
            filepath = os.path.join(dir_path, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                if is_approved:
                    f.write("APPROVED_BY: R.M.\n")
                    f.write("--- INTERNAL TX LOG ---\n")
                else:
                    if random.random() > 0.5:
                        f.write("DRAFT_MODE: UNVERIFIED\n")
                    # Some files might randomly start with garbage
                
                # Generate 1 to 5 transactions per file
                for _ in range(random.randint(1, 5)):
                    tx_id = f"TX_{tx_counter:04d}"
                    tx_counter += 1
                    
                    mat = random.choice(materials)
                    mat_id = mat["Material_ID"]
                    
                    qty = random.randint(1, 100)
                    
                    # Ensure we get some > 5000 prices for alerts
                    if random.random() < 0.05:
                        up = round(random.uniform(5001.0, 9999.0), 2)
                    else:
                        up = round(random.uniform(10.0, 800.0), 2)
                        
                    status = random.choice(["Received", "Pending", "Cancelled"])
                    
                    # Randomize spacing to simulate messy logs
                    sep = random.choice([" | ", "|", "  |  "])
                    line = f"TX: {tx_id}{sep}MAT: {mat_id}{sep}Q: {qty}{sep}UP: {up}{sep}STAT: {status}"
                    f.write(line + "\n")

if __name__ == "__main__":
    build_env()
