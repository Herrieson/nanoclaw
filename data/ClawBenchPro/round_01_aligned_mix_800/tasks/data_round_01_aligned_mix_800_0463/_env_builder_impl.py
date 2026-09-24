import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(42)
    
    # 1. Create Archives (Base Inventory)
    years = [2018, 2019, 2020, 2021, 2022]
    art_catalog = {} # id -> {title, price}
    
    for year in years:
        os.makedirs(f"archives/{year}/csv_dumps", exist_ok=True)
        os.makedirs(f"archives/{year}/json_dumps", exist_ok=True)
        
        # Generate 100 items per year
        csv_data = []
        json_data = []
        for i in range(100):
            art_id = f"ART-{year}{i:03d}"
            title = f"Artwork_{year}_{i}"
            
            # Dirty price formats
            raw_val = random.randint(100, 2000) + random.choice([0, 0.5])
            format_choice = random.choice([
                f"${raw_val}", 
                f"{raw_val} USD", 
                f"  {raw_val}  ", 
                f"USD {raw_val}"
            ])
            
            item = {"piece_id": art_id, "title": title, "price": format_choice}
            art_catalog[art_id] = {"title": title, "raw_val": float(raw_val)}
            
            if random.choice([True, False]):
                csv_data.append(item)
            else:
                json_data.append(item)
                
        # Write CSV
        with open(f"archives/{year}/csv_dumps/batch.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["piece_id", "title", "price"])
            writer.writeheader()
            writer.writerows(csv_data)
            
        # Write JSON (fragmented into multiple files)
        for idx, j_item in enumerate(json_data):
            with open(f"archives/{year}/json_dumps/item_{idx}.json", "w", encoding="utf-8") as f:
                json.dump(j_item, f)

    # 2. Create Status Logs
    os.makedirs("status_logs", exist_ok=True)
    
    # Generate chronological events
    # Rule: SOLD, GIFTED, DESTROYED -> unavailable
    # RETURNED -> available
    base_time = datetime(2023, 1, 1, 8, 0, 0)
    
    all_ids = list(art_catalog.keys())
    
    # We will pick 300 items to have status changes
    changed_ids = random.sample(all_ids, 300)
    
    # Create valid logs and decoy/draft logs
    valid_months = ["01", "02", "03", "04", "05"]
    
    for month in valid_months:
        log_lines = []
        # Add some noise lines
        log_lines.append("Remember to buy more yellow ochre paint.\n")
        log_lines.append("Call Dr. Adams about blurry vision.\n")
        
        # Add real events
        for _ in range(80):
            art_id = random.choice(changed_ids)
            status = random.choice(["SOLD", "GIFTED", "DESTROYED", "RETURNED"])
            # Some items get SOLD then RETURNED later because base_time advances
            base_time += timedelta(hours=random.randint(1, 24))
            ts_str = base_time.strftime("%Y-%m-%d %H:%M:%S")
            log_lines.append(f"[{ts_str}] | {art_id} | {status}\n")
            
        # Write valid log
        random.shuffle(log_lines)
        with open(f"status_logs/updates_2023_{month}.log", "w", encoding="utf-8") as f:
            f.writelines(log_lines)
            
        # Write decoy log (should be ignored based on prompt)
        decoy_lines = [f"[2099-01-01 00:00:00] | {random.choice(all_ids)} | DESTROYED\n"]
        with open(f"status_logs/draft_updates_{month}.log", "w", encoding="utf-8") as f:
            f.writelines(decoy_lines)
            
        with open(f"status_logs/error_log_{month}.txt", "w", encoding="utf-8") as f:
            f.writelines(decoy_lines)

if __name__ == "__main__":
    build_env()
