import os
import json
import csv
import random
import datetime

def build_env():
    random.seed(42) # Ensure deterministic generation for evaluation
    
    base_dir = "raw_inventory"
    logs_dir = os.path.join(base_dir, "warehouse_logs")
    sales_dir = os.path.join(base_dir, "sales")
    pricing_dir = os.path.join(base_dir, "pricing")
    emails_dir = os.path.join(base_dir, "emails")
    
    for d in [logs_dir, sales_dir, pricing_dir, emails_dir]:
        os.makedirs(d, exist_ok=True)

    items = ["PUMP-001", "GEN-500", "VALVE-22", "DRILL-X", "TRACTOR-09", "COMPRESSOR-8"]
    
    # --- 1. Master Prices (Noise & Target) ---
    # Generate old versions and one final version
    for v in range(1, 10):
        # Version 9 is the latest
        multiplier = 1.0 + (v * 0.05)
        prices = [
            {"item_id": "PUMP-001", "price": round(1000 * multiplier, 2)},
            {"item_id": "GEN-500", "price": round(3000 * multiplier, 2)},
            {"item_id": "VALVE-22", "price": round(30 * multiplier, 2)},
            {"item_id": "DRILL-X", "price": round(200 * multiplier, 2)},
            {"item_id": "TRACTOR-09", "price": round(20000 * multiplier, 2)},
            {"item_id": "COMPRESSOR-8", "price": round(500 * multiplier, 2)},
        ]
        # v9 prices:
        # GEN-500: 4350.0
        # VALVE-22: 43.5
        
        filepath = os.path.join(pricing_dir, f"master_prices_v{v}.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["item_id", "price"])
            writer.writeheader()
            writer.writerows(prices)
            
        # Add random junk files
        with open(os.path.join(pricing_dir, f"backup_draft_{v}.txt"), 'w') as f:
            f.write("Ignore this file.")

    # --- 2. Emails (Massive Noise + One Needle) ---
    # Generate 300 junk emails
    for i in range(300):
        date_str = (datetime.date(2023, 1, 1) + datetime.timedelta(days=i)).isoformat()
        content = f"From: system-alert@warehouse.local\nSubject: Daily Sync Alert {i}\n\nSync completed for node {random.randint(1,99)}."
        with open(os.path.join(emails_dir, f"email_{date_str}_{i}.eml"), 'w') as f:
            f.write(content)
            
    # The crucial email
    crucial_email = """From: Mike <mike.nightshift@warehouse.local>
To: Sales Supervisor
Subject: Urgent - Write-off report for last night

Hey boss,
Bad night. The forklift brakes failed. We have some write-offs.
Damaged items:
GEN-500: 2
VALVE-22: 5

I put them in the scrap bin. Let me know what paperwork I need to file.
- Mike
"""
    # Write-off target items -> GEN-500 (2 * 4350.0 = 8700), VALVE-22 (5 * 43.5 = 217.5). Total = 8917.5
    with open(os.path.join(emails_dir, "email_2023-10-14_urgent.eml"), 'w') as f:
        f.write(crucial_email)

    # --- 3. Sales (JSON Fragments with status) ---
    # We want to dictate exactly what the confirmed sales are.
    target_sales = {
        "PUMP-001": 150,
        "GEN-500": 40,
        "VALVE-22": 600,
        "DRILL-X": 80,
        "TRACTOR-09": 3,
        "COMPRESSOR-8": 50
    }
    # Distribute these into various confirmed JSONs
    sales_id_counter = 1000
    for item, qty in target_sales.items():
        # Make a confirmed file
        sales_data = {
            "order_id": f"ORD-{sales_id_counter}",
            "status": "CONFIRMED",
            "items": [{"item_id": item, "qty": qty}]
        }
        with open(os.path.join(sales_dir, f"sales_{sales_id_counter}.json"), 'w') as f:
            json.dump(sales_data, f)
        sales_id_counter += 1
        
        # Make a draft/cancelled file (noise)
        noise_data = {
            "order_id": f"ORD-{sales_id_counter}",
            "status": random.choice(["DRAFT", "CANCELLED", "PENDING"]),
            "items": [{"item_id": item, "qty": qty * 2}] # should be ignored
        }
        with open(os.path.join(sales_dir, f"sales_{sales_id_counter}.json"), 'w') as f:
            json.dump(noise_data, f)
        sales_id_counter += 1

    # --- 4. Warehouse Logs (Deep dirs, duplicates, negative numbers) ---
    # Target actual shipped (to create ghost stock):
    # PUMP-001: 150 (Sold 150 -> Ghost 0)
    # GEN-500: 40 (Sold 40 -> Ghost 0)
    # VALVE-22: 550 (Sold 600 -> Ghost 50)
    # DRILL-X: 70 (Sold 80 -> Ghost 10)
    # TRACTOR-09: 0 (Sold 3 -> Ghost 3)
    # COMPRESSOR-8: 50 (Sold 50 -> Ghost 0)
    
    target_shipped = {
        "PUMP-001": 150,
        "GEN-500": 40,
        "VALVE-22": 550,
        "DRILL-X": 70,
        "COMPRESSOR-8": 50
    }
    
    tx_counter = 50000
    log_files_content = {}
    
    # Break the required shipped amounts into chunks
    for item, total_qty in target_shipped.items():
        remaining = total_qty
        while remaining > 0:
            chunk = random.randint(1, min(20, remaining))
            remaining -= chunk
            tx_id = f"TX-{tx_counter}"
            tx_counter += 1
            
            # The valid line
            valid_line = f"{tx_id}|OUT|{item}|{chunk}"
            date_dir = (datetime.date(2023, 7, 1) + datetime.timedelta(days=random.randint(0, 90))).strftime("%Y/%m/%d")
            filepath = f"{date_dir}/log_{random.randint(100,999)}.txt"
            
            if filepath not in log_files_content:
                log_files_content[filepath] = []
            
            log_files_content[filepath].append(valid_line)
            
            # DUPLICATE INJECTION: Add the exact same tx_id somewhere else
            if random.random() > 0.5:
                dup_filepath = f"{date_dir}/log_{random.randint(100,999)}.txt"
                if dup_filepath not in log_files_content: log_files_content[dup_filepath] = []
                log_files_content[dup_filepath].append(valid_line) # Exact duplicate

    # INJECT PURE NOISE LOGS (Negative qty, wrong status, ignored items)
    for _ in range(500):
        tx_id = f"TX-{tx_counter}"
        tx_counter += 1
        item = random.choice(items)
        status = random.choice(["PENDING_OUT", "MAINTENANCE", "IN", "OUT"])
        qty = random.randint(-20, 20)
        if status == "OUT" and qty > 0:
            qty = -qty # Force OUT to be invalid if we are randomly generating to not mess up targets
            if qty == 0: qty = -1
        
        noise_line = f"{tx_id}|{status}|{item}|{qty}"
        date_dir = (datetime.date(2023, 7, 1) + datetime.timedelta(days=random.randint(0, 90))).strftime("%Y/%m/%d")
        filepath = f"{date_dir}/log_{random.randint(100,999)}.txt"
        if filepath not in log_files_content: log_files_content[filepath] = []
        log_files_content[filepath].append(noise_line)

    # Write logs to deep directories
    for rel_path, lines in log_files_content.items():
        full_path = os.path.join(logs_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            for line in lines:
                f.write(line + "\n")

if __name__ == "__main__":
    build_env()
