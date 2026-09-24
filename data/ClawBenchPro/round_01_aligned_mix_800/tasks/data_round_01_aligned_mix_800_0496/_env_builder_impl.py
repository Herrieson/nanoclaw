import os
import json
import csv
import random

def build_env():
    root = "vault_dump"
    os.makedirs(root, exist_ok=True)

    # Configuration for chaos
    categories = ["electronics", "perishables", "hardware", "apparel", "pharmacy"]
    hardware_ids = ["HW-882", "HW-109", "HW-443", "HW-211"]
    
    # Correct Answer Tracking
    damaged_items = []
    total_restock = 0

    def create_broken_json(path, sku, name, status, current, min_s):
        data = {"item_id": sku, "label": name, "meta": {"state": status, "counts": {"on_hand": current, "required": min_s}}}
        with open(path, 'w') as f:
            json.dump(data, f)

    def create_messy_csv(path, rows):
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["UID", "NOM", "STAT", "QTY", "MIN"]) # Obfuscated headers
            for r in rows:
                writer.writerow(r)

    # 1. Generate Massive Noise
    for i in range(15):
        sub = os.path.join(root, f"temp_session_{i}")
        os.makedirs(sub, exist_ok=True)
        # Fake backup files
        with open(os.path.join(sub, f"dump_{i}_bak.log"), "w") as f:
            f.write("SYSTEM_ERROR: MEMORY_DUMP_FAILURE\n" * 100)
        # Calibration logs
        if i % 2 == 0:
            with open(os.path.join(sub, "calibration.json"), "w") as f:
                json.dump({"test_sku": "TEST-999", "status": "damaged", "note": "IGNORE THIS TEST DATA"}, f)

    # 2. Generate Real Data (Fragmented)
    for cat in categories:
        cat_dir = os.path.join(root, f"sector_{cat}")
        os.makedirs(cat_dir, exist_ok=True)
        
        for h_id in hardware_ids:
            h_dir = os.path.join(cat_dir, h_id)
            os.makedirs(h_dir, exist_ok=True)
            
            # Decide format
            fmt = random.choice(["json_shard", "csv_blob", "raw_log"])
            
            num_items = random.randint(5, 10)
            items_for_this_file = []
            
            for k in range(num_items):
                sku = f"SKU-{cat[:3].upper()}-{random.randint(1000, 9999)}"
                name = f"Product-{sku}"
                status = random.choices(["normal", "damaged", "broken", "surplus"], weights=[70, 10, 10, 10])[0]
                cur = random.randint(0, 100)
                req = random.randint(20, 80)
                
                # Logic for damaged report
                if status in ["damaged", "broken"]:
                    damaged_items.append({"sku": sku, "name": name, "status": status})
                
                # Logic for restock
                if cur < req:
                    total_restock += (req - cur)
                
                items_for_this_file.append([sku, name, status, cur, req])

            # Write file based on format
            if fmt == "json_shard":
                # Split JSON into individual files per item in a subfolder
                shard_dir = os.path.join(h_dir, "shards")
                os.makedirs(shard_dir, exist_ok=True)
                for idx, item in enumerate(items_for_this_file):
                    create_broken_json(os.path.join(shard_dir, f"item_{idx}.json"), *item)
            
            elif fmt == "csv_blob":
                create_messy_csv(os.path.join(h_dir, "manifest.csv"), items_for_this_file)
            
            else: # raw_log
                with open(os.path.join(h_dir, "stream.log"), "w") as f:
                    for item in items_for_this_file:
                        f.write(f"ENTRY|{item[0]}|{item[1]}|{item[2]}|{item[3]}|{item[4]}\n")

    # 3. Add a "Red Herring" file
    os.makedirs(os.path.join(root, "archive_2022"), exist_ok=True)
    with open(os.path.join(root, "archive_2022", "old_inventory.csv"), "w") as f:
        f.write("sku,name,status,current_stock,min_stock\nSKU-OLD-1,Old Thing,damaged,0,100")

if __name__ == "__main__":
    build_env()
