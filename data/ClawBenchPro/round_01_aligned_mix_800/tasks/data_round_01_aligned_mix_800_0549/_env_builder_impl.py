import os
import json
import csv
import random
import uuid
from datetime import datetime, timedelta

def build_env():
    # Set a fixed seed for reproducible "chaos"
    random.seed(1271)

    # 1. Create directory structures
    os.makedirs("requests", exist_ok=True)
    os.makedirs("warehouse_logs", exist_ok=True)
    os.makedirs("reference", exist_ok=True)

    # 2. Generate Master Data (SKUs and Schools)
    items_pool = [
        "No. 2 Pencils (Box)", "Notebooks", "Binders", "Calculators", 
        "Erasers", "Rulers", "Highlighters", "Whiteboard Markers", 
        "Staplers", "Glue Sticks", "Scissors", "Construction Paper",
        "Index Cards", "Sticky Notes", "Hand Sanitizer", "Tissues"
    ]
    art_items = ["Acrylic Paint", "Blank Canvas"]
    all_items = items_pool + art_items

    sku_master = []
    item_to_sku = {}
    for idx, item in enumerate(all_items):
        sku = f"SKU-100{idx:03d}"
        sku_master.append([sku, item, "Art" if item in art_items else "General"])
        item_to_sku[item] = sku

    with open("reference/sku_master.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["SKU", "Item_Name", "Category"])
        writer.writerows(sku_master)

    schools = []
    for i in range(1, 101):
        code = f"SCH-90{i:03d}"
        name = f"{random.choice(['Oakridge', 'Pine View', 'Cedar', 'Maple', 'Willow', 'Lincoln', 'Washington', 'Roosevelt', 'Kennedy'])} {random.choice(['Elementary', 'Middle', 'High', 'Academy', 'Prep'])} {i}"
        schools.append({"school_code": code, "school_name": name, "district": f"District {random.randint(1, 5)}"})

    with open("reference/school_registry.json", "w") as f:
        json.dump(schools, f, indent=2)

    # 3. Generate Requests
    # Select 25 schools to have APPROVED requests. Others will have REJECTED, PENDING, or no requests.
    approved_schools = random.sample(schools, 25)
    art_school_codes = []

    # Generate the noise and actual requests
    for school in schools:
        num_requests = random.randint(1, 3)
        for r_idx in range(num_requests):
            is_approved_req = (school in approved_schools) and (r_idx == 0) # Only one approved request per approved school
            status = "APPROVED" if is_approved_req else random.choice(["REJECTED", "PENDING", "DRAFT"])
            
            req_items = {}
            # Ensure some approved schools request art items
            if is_approved_req and random.random() < 0.3:
                art_school_codes.append(school["school_code"])
                req_items[random.choice(art_items)] = random.randint(5, 20)
                if random.random() < 0.5:
                    req_items[art_items[0] if req_items.keys() != art_items[0] else art_items[1]] = random.randint(5, 20)
            
            # General items
            for _ in range(random.randint(2, 6)):
                req_items[random.choice(items_pool)] = random.randint(10, 100)
            
            file_data = {
                "request_id": str(uuid.uuid4()),
                "school_code": school["school_code"],
                "status": status,
                "requested_items": req_items,
                "submitted_by": f"Rep_{random.randint(1,99)}"
            }

            # Write to different file formats and extensions to create fragmentation
            ext = random.choice([".json", ".json", ".json", ".bak", ".tmp"])
            filename = f"requests/req_{school['school_code'].lower()}_{uuid.uuid4().hex[:6]}{ext}"
            
            if ext == ".json":
                with open(filename, "w") as f:
                    json.dump(file_data, f, indent=2)
            else:
                with open(filename, "w") as f:
                    f.write(json.dumps(file_data)) # Minified for non-json extensions just to be annoying

    # 4. Generate Warehouse Logs across a nested directory tree
    start_date = datetime(2023, 10, 1)
    
    # We need to track how much we are "shipping" vs "returning" to guarantee some missing items
    # and some perfectly fulfilled ones for the approved schools.
    logs_to_write = []
    
    for school in approved_schools:
        # Re-read their approved request to know what to ship
        # In this builder context we just rebuild the math
        # Actually, let's find the exact approved request we generated
        # to ensure perfect consistency.
        pass

    # Better approach to guarantee exact warehouse logs matching the generated approved requests:
    approved_reqs_cache = []
    for root, dirs, files in os.walk("requests"):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "r") as f:
                    try:
                        data = json.load(f)
                        if data.get("status") == "APPROVED":
                            approved_reqs_cache.append(data)
                    except:
                        pass
    
    for req in approved_reqs_cache:
        s_code = req["school_code"]
        for item, req_qty in req["requested_items"].items():
            sku = item_to_sku[item]
            
            # Determine fulfillment strategy for this item
            strat = random.choice(["PERFECT", "SHORT", "EXCESS", "MESSY_SHORT"])
            
            net_needed = req_qty
            if strat == "PERFECT":
                shipped = req_qty
                returned = 0
            elif strat == "SHORT":
                shipped = req_qty - random.randint(1, max(1, req_qty - 1))
                returned = 0
            elif strat == "EXCESS":
                shipped = req_qty + random.randint(5, 10)
                returned = 0
            else: # MESSY_SHORT
                shipped = req_qty + random.randint(5, 10)
                returned = shipped - req_qty + random.randint(1, 5) # ultimately short

            # Create log entries
            if shipped > 0:
                # Split shipped into multiple chunks randomly
                chunks = [shipped // 2, shipped - (shipped // 2)]
                for c in chunks:
                    if c > 0:
                        logs_to_write.append({
                            "date": start_date + timedelta(days=random.randint(0, 20)),
                            "s_code": s_code, "sku": sku, "qty": c, "status": "SHIPPED"
                        })
            
            if returned > 0:
                logs_to_write.append({
                    "date": start_date + timedelta(days=random.randint(21, 28)), # Returns happen later
                    "s_code": s_code, "sku": sku, "qty": returned, "status": "RETURNED"
                })

    # Add massive noise: random shipments, cancelled orders, processing states for non-approved schools
    for _ in range(2000):
        logs_to_write.append({
            "date": start_date + timedelta(days=random.randint(0, 30)),
            "s_code": random.choice(schools)["school_code"],
            "sku": random.choice(sku_master)[0],
            "qty": random.randint(1, 50),
            "status": random.choice(["SHIPPED", "RETURNED", "PROCESSING", "CANCELLED", "SHIPPED"]) # Weight shipped
        })

    # Distribute logs into daily CSVs
    daily_logs = {}
    for log in logs_to_write:
        d_str = log["date"].strftime("%Y/%m/%d")
        if d_str not in daily_logs:
            daily_logs[d_str] = []
        daily_logs[d_str].append(log)

    for d_str, entries in daily_logs.items():
        dir_path = os.path.join("warehouse_logs", d_str)
        os.makedirs(dir_path, exist_ok=True)
        
        # shuffle entries
        random.shuffle(entries)
        
        file_path = os.path.join(dir_path, f"manifest_{uuid.uuid4().hex[:8]}.csv")
        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Transaction_ID", "Timestamp", "School_Code", "SKU", "Qty", "Status"])
            for e in entries:
                txn = f"TXN-{uuid.uuid4().hex[:10].upper()}"
                ts = e["date"].strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([txn, ts, e["s_code"], e["sku"], e["qty"], e["status"]])

if __name__ == "__main__":
    build_env()
