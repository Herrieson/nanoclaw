import os
import sqlite3
import json
import random
from datetime import datetime, timedelta

def setup_environment():
    base_path = "assets/data_425"
    os.makedirs(f"{base_path}/audit_dropzone", exist_ok=True)

    # 1. Create SQLite DB for Exchange Rates (CAD to USD)
    db_path = os.path.join(base_path, "daily_exchange_rates.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE rates (date TEXT PRIMARY KEY, cad_to_usd REAL)")
    
    start_date = datetime(2023, 7, 1)
    rates = {}
    for i in range(92): # Q3
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        rate = round(0.73 + random.uniform(-0.02, 0.02), 4)
        rates[date_str] = rate
        cursor.execute("INSERT INTO rates VALUES (?, ?)", (date_str, rate))
    conn.commit()
    conn.close()

    # 2. Create Master Vendor List
    vendors = [
        {"id": "V001", "name": "Global Produce", "tax_id": "TX-9981"},
        {"id": "V002", "name": "Maple Leaf Logistics", "tax_id": "TX-4421"},
        {"id": "V003", "name": "Oceanic Seafood", "tax_id": "TX-1120"}
    ]
    with open(f"{base_path}/master_vendors.json", "w") as f:
        json.dump(vendors, f)

    # 3. Create Transaction Logs with traps
    transactions = []
    total_forex_loss = 0
    unauthorized_total = 0
    flagged_ids = []

    # Issue 1: Forex Discrepancy (Maple Leaf Logistics)
    # Target discrepancy total: 14215.30
    # Let's split it: Forex loss = 8215.30, Unauthorized = 6000.00
    
    # Generate Forex errors
    for i in range(5):
        date_str = (start_date + timedelta(days=random.randint(0, 80))).strftime("%Y-%m-%d")
        cad_amount = 10000.0
        correct_usd = round(cad_amount * rates[date_str], 2)
        error_amount = 1643.06 # Fixed error per transaction to reach 8215.30 in 5 steps
        recorded_usd = round(correct_usd + error_amount, 2)
        
        tx_id = f"TXN_FX_{i}"
        transactions.append({
            "id": tx_id,
            "date": date_str,
            "vendor": "Maple Leaf Logistics",
            "amount_cad": cad_amount,
            "recorded_usd": recorded_usd
        })
        total_forex_loss += error_amount
        flagged_ids.append(tx_id)

    # Issue 2: Unauthorized Vendor
    for i in range(3):
        tx_id = f"TXN_UA_{i}"
        amount = 2000.0
        transactions.append({
            "id": tx_id,
            "date": "2023-08-15",
            "vendor": "Apex Quality Meats",
            "recorded_usd": amount
        })
        unauthorized_total += amount
        flagged_ids.append(tx_id)

    # Add 100 noise transactions
    for i in range(100):
        transactions.append({
            "id": f"TXN_NORM_{i}",
            "date": (start_date + timedelta(days=random.randint(0, 80))).strftime("%Y-%m-%d"),
            "vendor": "Global Produce",
            "recorded_usd": round(random.uniform(100, 500), 2)
        })

    random.shuffle(transactions)
    with open(f"{base_path}/q3_procurement_logs.json", "w") as f:
        json.dump(transactions, f)

    # 4. Create a mock tool for Tax ID verification
    with open(f"{base_path}/calc_tax_id", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("if [ \"$1\" == \"Apex Quality Meats\" ]; then echo \"INVALID: NO REGISTERED TAX ID\"; else echo \"VALID\"; fi")
    os.chmod(f"{base_path}/calc_tax_id", 0o755)

if __name__ == "__main__":
    setup_environment()
