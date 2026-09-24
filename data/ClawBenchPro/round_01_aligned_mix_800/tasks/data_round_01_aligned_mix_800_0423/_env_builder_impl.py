import os
import json
import random
import csv
from datetime import datetime, timedelta

def build_env():
    # 🚨 Asset path is current working directory
    
    # --- Part 1: Fragmented Invoices ---
    invoice_dir = "archives/billing/invoices"
    os.makedirs(invoice_dir, exist_ok=True)
    
    # The "Truth" Data
    master_invoices = [
        {"id": "V-9921", "vendor": "Green Valley Organics", "items": [
            {"sku": "AVO-01", "name": "Organic Avocados", "qty": 100, "price": 2.50},
            {"sku": "SOU-02", "name": "Artisan Sourdough", "qty": 50, "price": 8.00}
        ]},
        {"id": "V-4410", "vendor": "EuroImports", "items": [
            {"sku": "MAN-09", "name": "Manchego Cheese (lbs)", "qty": 40, "price": 15.00},
            {"sku": "TRF-05", "name": "Truffle Oil", "qty": 24, "price": 25.00}
        ]},
        {"id": "V-1002", "vendor": "Spice Road", "items": [
            {"sku": "TOM-99", "name": "Heirloom Tomatoes", "qty": 200, "price": 3.00},
            {"sku": "SAF-88", "name": "Saffron (oz)", "qty": 5, "price": 120.00}
        ]}
    ]

    # Shred invoices into multiple files
    for inv in master_invoices:
        # Split each invoice into header and items
        with open(f"{invoice_dir}/head_{inv['id']}.json", "w") as f:
            json.dump({"id": inv['id'], "vendor": inv['vendor']}, f)
        
        for item in inv['items']:
            with open(f"{invoice_dir}/item_{inv['id']}_{item['sku']}.fragment", "w") as f:
                f.write(f"SKU: {item['sku']}|NAME: {item['name']}|QTY: {item['qty']}|UPRICE: {item['price']}")

    # Add 100 decoy files in billing
    for i in range(100):
        with open(f"{invoice_dir}/trash_{i}.tmp", "w") as f:
            f.write("DELETED_RECORD_" + str(random.random()))

    # --- Part 2: Chaotic Inventory Logs ---
    log_dir = "logs/inventory/night_shift"
    os.makedirs(log_dir, exist_ok=True)

    # Actual Received Quantities (The "Shortage" Logic)
    # AVO: 90 (Short 10 * 2.5 = 25)
    # SOU: 50 (OK)
    # MAN: 35 (Short 5 * 15 = 75)
    # TRF: 24 (OK)
    # TOM: 210 (Extra 10 - Ignore)
    # SAF: 2 (Short 3 * 120 = 360)
    # Total Shortage Expected: 25 + 75 + 360 = 460.00

    actual_received = {
        "AVO-01": 90,
        "SOU-02": 50,
        "MAN-09": 35,
        "TRF-05": 24,
        "TOM-99": 210,
        "SAF-88": 2
    }

    # Generate many hourly logs, but only files with "FINAL" in name and valid timestamp are real
    base_time = datetime(2023, 10, 25, 22, 0, 0)
    
    skus = list(actual_received.keys())
    for hour in range(8):
        current_time = base_time + timedelta(hours=hour)
        ts_str = current_time.strftime("%H%M")
        
        # Real log
        log_name = f"log_TS{ts_str}_FINAL.csv"
        with open(f"{log_dir}/{log_name}", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["entry_id", "item_ref", "count"])
            # Distribute items randomly across hours
            for _ in range(3):
                target_sku = random.choice(skus)
                # Just a portion of the total
                amt = random.randint(1, 5)
                writer.writerow([random.randint(1000, 9999), target_sku, amt])
        
        # Decoy "Draft" logs
        with open(f"{log_dir}/log_TS{ts_str}_DRAFT.csv", "w") as f:
            f.write("IGNORE THIS DATA, MISTAKE IN COUNTING")

    # To ensure the totals match exactly for the agent, we'll overwrite one "FINAL" log 
    # with the actual remaining balances to make the math deterministic.
    final_adjustment_log = "log_TS0600_FINAL.csv"
    current_counts = {sku: 0 for sku in skus}
    # (Simulate the aggregation to find remainder)
    for file in os.listdir(log_dir):
        if "FINAL" in file:
            with open(os.path.join(log_dir, file), 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    current_counts[row['item_ref']] += int(row['count'])
    
    with open(f"{log_dir}/{final_adjustment_log}", "a", newline="") as f:
        writer = csv.writer(f)
        for sku, total_needed in actual_received.items():
            diff = total_needed - current_counts[sku]
            if diff != 0:
                writer.writerow(["ADJUST", sku, diff])

    # Add 200 dummy files in logs
    for i in range(200):
        with open(f"{log_dir}/backup_node_{i}.log", "w") as f:
            f.write("HEARTBEAT OK")

if __name__ == "__main__":
    build_env()
