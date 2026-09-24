import os
import json
import csv
import random
import math

def build_env():
    # Set up random seed for reproducibility
    random.seed(1647)
    
    # 1. Create directory structures
    os.makedirs("reference_guide", exist_ok=True)
    os.makedirs("safety_clearance", exist_ok=True)
    
    # 2. Build material dictionary
    base_materials = {
        "Wood": ["Reclaimed Wood Planks", "Oak Wood Chips", "Birch Wood Panels", "Scrap Wood Pieces", "Mahogany Wood Carvings"],
        "Fabric": ["Organic Cotton Fabric", "Old Denim Fabric", "Silk Fabric Scraps", "Polyester Fabric Rolls", "Wool Fabric Bundle"],
        "Glass": ["Recycled Glass Bottles", "Shattered Glass Mosaic", "Stained Glass Sheets", "Clear Glass Jars"],
        "Toxic_Wood": ["Lead-painted Wood Panels", "PVC-coated Wood", "Wood with Styrofoam packaging"],
        "Toxic_Fabric": ["Fabric with Lead weights", "PVC threaded Fabric"],
        "Toxic_Glass": ["Lead Crystal Glass", "Glass packaged in Styrofoam"],
        "Noise": ["Steel Pipes", "Aluminum Cans", "Concrete Blocks", "Cardboard Boxes", "Plastic Toys", "Ceramic Tiles", "Rubber Tires"]
    }
    
    material_dict = {}
    code_counter = 100
    category_mapping = {}
    
    for category, names in base_materials.items():
        for name in names:
            code = f"MAT-{code_counter}"
            material_dict[code] = name
            category_mapping[code] = category
            code_counter += 1
            
    with open(os.path.join("reference_guide", "materials.json"), "w") as f:
        json.dump(material_dict, f, indent=4)
        
    # 3. Build safety clearance DB
    statuses = ["APPROVED", "REJECTED", "PENDING", "QUARANTINED"]
    clearance_data = [["batch_id", "inspector_name", "status", "date"]]
    batch_status_map = {}
    
    for i in range(1, 501):
        batch_id = f"BATCH-{i:04d}"
        status = random.choices(statuses, weights=[0.3, 0.4, 0.2, 0.1])[0]
        batch_status_map[batch_id] = status
        clearance_data.append([batch_id, f"Inspector_{random.randint(1,20)}", status, f"2023-10-{random.randint(1,31):02d}"])
        
    with open(os.path.join("safety_clearance", "clearance_db.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(clearance_data)
        
    # 4. Build fragmented inventory logs
    regions = ["90210", "10001", "33101", "94105", "60601"]
    
    for i in range(1, 501):
        batch_id = f"BATCH-{i:04d}"
        region = random.choice(regions)
        date = f"2023-10-{random.randint(1,31):02d}"
        
        dir_path = os.path.join("inventory_logs", region, date)
        os.makedirs(dir_path, exist_ok=True)
        
        num_items = random.randint(3, 15)
        records = []
        for _ in range(num_items):
            # 5% chance of invalid/unknown code
            if random.random() < 0.05:
                m_code = f"MAT-{random.randint(900, 999)}"
            else:
                m_code = random.choice(list(material_dict.keys()))
                
            qty = round(random.uniform(1.0, 50.0), 2)
            unit = random.choice(["kg", "lbs", "oz"])
            records.append({"code": m_code, "qty": qty, "unit": unit})
            
        file_format = random.choice(["json", "csv"])
        
        if file_format == "json":
            file_path = os.path.join(dir_path, f"{batch_id}.json")
            # Embed batch_id inside the json
            data = {"batch_reference": batch_id, "warehouse_notes": "Random notes", "items": records}
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            file_path = os.path.join(dir_path, f"{batch_id}.csv")
            with open(file_path, "w", newline="") as f:
                # Add messy headers
                f.write(f"# This is a system generated log for {batch_id}\n")
                f.write(f"# DO NOT MODIFY THIS FILE\n")
                f.write(f"batch_id,{batch_id},,\n")
                writer = csv.writer(f)
                writer.writerow(["material_code", "quantity", "weight_unit"])
                for r in records:
                    writer.writerow([r["code"], r["qty"], r["unit"]])

if __name__ == "__main__":
    build_env()
