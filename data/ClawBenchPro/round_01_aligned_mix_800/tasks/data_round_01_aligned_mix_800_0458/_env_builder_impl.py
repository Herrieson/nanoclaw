import os
import json
import csv
import random

def build_env():
    random.seed(1191)
    base_dir = 'supplier_dumps'
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create config files (The decoders)
    config_dir = os.path.join(base_dir, 'system_config')
    os.makedirs(config_dir, exist_ok=True)
    
    category_map = {
        "CAT-S01": "Solar",
        "CAT-S02": "Solar",
        "CAT-W99": "Wind",
        "CAT-H00": "Hydroponic",
        "CAT-F01": "Fossil",
        "CAT-F02": "Fossil",
        "CAT-X99": "Misc"
    }
    with open(os.path.join(config_dir, 'category_map.json'), 'w') as f:
        json.dump(category_map, f, indent=2)
        
    status_codes = [
        {"code": "100", "meaning": "New"},
        {"code": "101", "meaning": "Like New"},
        {"code": "200", "meaning": "Refurbished"},
        {"code": "201", "meaning": "Used"},
        {"code": "500", "meaning": "Damaged"},
        {"code": "501", "meaning": "Damaged"}, # Multiple codes can mean Damaged
        {"code": "900", "meaning": "Lost"}
    ]
    with open(os.path.join(config_dir, 'status_codes.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["code", "meaning"])
        writer.writeheader()
        writer.writerows(status_codes)

    # 2. Generate fragmented data across years and suppliers
    suppliers = ['ApexCorp', 'BioTech', 'SunEnergy_Global']
    years_months = ['2023-11', '2023-12', '2024-01', '2024-02', '2024-03']
    
    item_counter = 1
    
    for supplier in suppliers:
        for ym in years_months:
            # Create deeply nested directory
            dir_path = os.path.join(base_dir, supplier, ym, 'manifests')
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate 20-50 files per directory
            num_files = random.randint(20, 50)
            
            for _ in range(num_files):
                # Randomize if this item will be valid or invalid
                cat_code = random.choice(list(category_map.keys()))
                status_code = random.choice([s['code'] for s in status_codes])
                
                # Prices with noise
                raw_price = round(random.uniform(-500, 5000), 2)
                if random.random() < 0.1:
                    price_str = "" # missing price
                else:
                    # formatting with currencies and commas
                    if random.random() < 0.5:
                        price_str = f"${raw_price:,.2f}"
                    else:
                        price_str = f"€{raw_price:,.2f}"
                
                item_id = f"ITM-{item_counter:05d}"
                desc = f"Equipment component {cat_code}-{status_code}"
                
                data_dict = {
                    "id": item_id,
                    "desc": desc,
                    "cat_code": cat_code,
                    "status_code": int(status_code) if random.random() < 0.5 else status_code, # mix types
                    "cost": price_str
                }
                
                # Mix JSON and CSV formats for fragmentation
                file_format = random.choice(['json', 'csv'])
                file_name = f"record_{item_id}.{file_format}"
                file_path = os.path.join(dir_path, file_name)
                
                if file_format == 'json':
                    with open(file_path, 'w') as f:
                        json.dump(data_dict, f)
                else:
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["id", "desc", "cat_code", "status_code", "cost"])
                        writer.writerow([data_dict["id"], data_dict["desc"], data_dict["cat_code"], data_dict["status_code"], data_dict["cost"]])
                
                item_counter += 1

if __name__ == "__main__":
    build_env()
