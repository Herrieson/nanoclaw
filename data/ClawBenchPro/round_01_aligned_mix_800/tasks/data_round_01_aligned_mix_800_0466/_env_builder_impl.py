import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Directories
    os.makedirs("raw_records/attendance_scans", exist_ok=True)
    os.makedirs("raw_records/consent_webhooks", exist_ok=True)
    os.makedirs("raw_records/finance", exist_ok=True)
    os.makedirs("raw_records/vendor_specs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Base Data Generation
    random.seed(42) # Ensure determinism
    
    users = []
    names = ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Evan Wright", 
             "Frank Ocean", "Grace Hopper", "Hank Pym", "Ivy Chen", "Jack O'Neill",
             "Karen Page", "Leo Fitz", "Mia Wallace", "Nathan Drake", "Olivia Pope",
             "Peter Parker", "Quinn Fabray", "Rachel Green", "Steve Rogers", "Tony Stark",
             "Uma Thurman", "Victor Stone", "Wanda Maximoff", "Xander Harris", "Yelena Belova"]
    
    for i, name in enumerate(names):
        users.append({
            "uid": f"USR_{1000 + i}",
            "name": name,
            "attended": random.choice([True, True, False]), # More likely to attend
            "final_consent": random.choice(["SIGNED", "REVOKED", "PENDING", None])
        })

    # 1. Build Attendance Scans (Noise + Fragmentation)
    stations = ["station_alpha.log", "station_beta.log", "station_gamma.log", "station_delta.log"]
    station_files = {s: open(f"raw_records/attendance_scans/{s}", "w", encoding="utf-8") for s in stations}
    
    base_time = datetime(2023, 10, 15, 8, 0, 0)
    for u in users:
        # Generate some VOID scans for everyone just to add noise
        num_voids = random.randint(0, 3)
        for _ in range(num_voids):
            t = base_time + timedelta(minutes=random.randint(0, 300))
            sf = random.choice(list(station_files.values()))
            sf.write(f"{t.isoformat()} | VOID | {u['uid']} | {u['name']}\n")
        
        # If they actually attended, write a SUCCESS scan
        if u["attended"]:
            t = base_time + timedelta(minutes=random.randint(0, 300))
            sf = random.choice(list(station_files.values()))
            sf.write(f"{t.isoformat()} | SUCCESS | {u['uid']} | {u['name']}\n")
            
    for sf in station_files.values():
        sf.close()

    # 2. Build Consent Webhooks (Scale + Temporal Logic + Noise)
    webhook_counter = 1
    base_webhook_time = datetime(2023, 10, 1, 10, 0, 0)
    
    def write_webhook(event_type, uid, status, t):
        nonlocal webhook_counter
        payload = {
            "event_id": f"EVT_{webhook_counter:05d}",
            "type": event_type,
            "user_id": uid,
            "timestamp": t.isoformat()
        }
        if event_type == "CONSENT_UPDATE":
            payload["status"] = status
        else:
            payload["campaign"] = "Winter_Newsletter"
            
        with open(f"raw_records/consent_webhooks/hook_{webhook_counter:04d}.json", "w", encoding="utf-8") as f:
            json.dump(payload, f)
        webhook_counter += 1

    # Generate massive noise events
    for _ in range(150):
        t = base_webhook_time + timedelta(days=random.randint(0, 10), minutes=random.randint(0, 1000))
        write_webhook("NEWSLETTER_SIGNUP", f"USR_{random.randint(1000, 1024)}", None, t)

    # Generate consent history
    for u in users:
        if u["final_consent"] is None:
            continue
            
        # Give them 1-3 previous statuses before the final one
        num_history = random.randint(0, 2)
        current_time = base_webhook_time + timedelta(days=random.randint(0, 5))
        
        for _ in range(num_history):
            temp_status = random.choice(["PENDING", "REVOKED", "SIGNED"])
            write_webhook("CONSENT_UPDATE", u["uid"], temp_status, current_time)
            current_time += timedelta(hours=random.randint(1, 48))
            
        # Write the final status
        write_webhook("CONSENT_UPDATE", u["uid"], u["final_consent"], current_time)

    # 3. Build Eco Catalog
    items = []
    eco_catalog = {}
    for i in range(1, 31):
        item_id = f"ITEM_{2000+i}"
        is_sus = random.choice([True, False])
        price = round(random.uniform(10.0, 500.0), 2)
        eco_catalog[item_id] = {
            "description": f"Event Supply {i}",
            "is_sustainable": is_sus,
            "base_price": price
        }
        items.append(item_id)
        
    with open("raw_records/vendor_specs/eco_catalog.json", "w", encoding="utf-8") as f:
        json.dump(eco_catalog, f, indent=4)

    # 4. Build Finance CSVs (Multiple quarters, different events, mapping required)
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    for q in quarters:
        with open(f"raw_records/finance/expenses_{q}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["TransactionID", "EventCode", "ItemID", "Quantity", "UnitPrice"])
            
            for i in range(80): # 80 transactions per quarter
                t_id = f"TXN_{q}_{i:03d}"
                # Mix of target event and noise events
                event_code = "VS_2023" if random.random() > 0.75 else f"OTHER_EVT_{random.randint(1,5)}"
                item_id = random.choice(items)
                qty = random.randint(1, 10)
                unit_price = eco_catalog[item_id]["base_price"]
                writer.writerow([t_id, event_code, item_id, qty, f"{unit_price:.2f}"])

if __name__ == "__main__":
    build_env()
