import os
import json
import csv
import sqlite3
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(42) # Ensure deterministic generation

    # 1. Create directory structures
    dirs = [
        "archives/contracts_2022",
        "archives/contracts_2023",
        "payment_gateways/stripe",
        "payment_gateways/bank",
        "payment_gateways/cash",
        "deliverables"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Helper: Generate names
    first_names = ["James", "Linda", "Sarah", "Robert", "Gina", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    names = list(set([f"{f} {l}" for f in first_names for l in last_names]))
    random.shuffle(names)

    # 2. Build Database for Sustainability (Multi-hop DB logic)
    conn = sqlite3.connect("property_specs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE units (unit_id TEXT, hvac_model_id TEXT)")
    cursor.execute("CREATE TABLE hvac_specs (model_id TEXT, energy_tier TEXT)")

    hvac_models = [f"HVAC-{str(i).zfill(3)}" for i in range(1, 11)]
    # Tier-1 to Tier-5. Tier 4 and 5 are targets.
    hvac_tiers = {
        "HVAC-001": "Tier-1", "HVAC-002": "Tier-2", "HVAC-003": "Tier-1",
        "HVAC-004": "Tier-4", "HVAC-005": "Tier-3", "HVAC-006": "Tier-5",
        "HVAC-007": "Tier-2", "HVAC-008": "Tier-4", "HVAC-009": "Tier-3",
        "HVAC-010": "Tier-5"
    }
    cursor.executemany("INSERT INTO hvac_specs VALUES (?, ?)", list(hvac_tiers.items()))

    # Generate 250 units
    units = [f"U-{str(i).zfill(4)}" for i in range(1, 251)]
    unit_hvac_mapping = [(u, random.choice(hvac_models)) for u in units]
    cursor.executemany("INSERT INTO units VALUES (?, ?)", unit_hvac_mapping)
    conn.commit()
    conn.close()

    # 3. Generate Contracts and Noise
    # 200 Active Contracts in 2023
    active_tenants = []
    for i in range(1, 201):
        t_id = f"T-{str(i).zfill(4)}"
        t_name = names.pop()
        unit = units[i-1]
        rent = random.choice([1000, 1200, 1500, 1800, 2000, 2500])
        contract = {
            "tenant_id": t_id,
            "name": t_name,
            "unit_id": unit,
            "monthly_rent": rent,
            "status": "ACTIVE",
            "signed_date": f"2023-01-{random.randint(10, 28)}"
        }
        active_tenants.append(contract)
        with open(f"archives/contracts_2023/contract_{t_id}.json", "w") as f:
            json.dump(contract, f, indent=4)

    # 50 Terminated/Draft Contracts in 2023 (Noise)
    for i in range(201, 251):
        t_id = f"T-{str(i).zfill(4)}"
        contract = {
            "tenant_id": t_id,
            "name": names.pop(),
            "unit_id": random.choice(units),
            "monthly_rent": 1500,
            "status": random.choice(["TERMINATED", "DRAFT"])
        }
        with open(f"archives/contracts_2023/contract_{t_id}_old.json", "w") as f:
            json.dump(contract, f, indent=4)

    # 200 Contracts in 2022 (Noise)
    for i in range(301, 501):
        t_id = f"T-{str(i).zfill(4)}"
        with open(f"archives/contracts_2022/contract_{t_id}.json", "w") as f:
            json.dump({"tenant_id": t_id, "status": "ACTIVE", "year": 2022}, f)

    # 4. Generate Payments (Fragmented & Noisy)
    all_payments = []
    
    # Target period: Q3 (July, Aug, Sept 2023)
    q3_months = ["2023-07", "2023-08", "2023-09"]
    other_months = ["2023-01", "2023-02", "2023-05", "2023-10", "2023-11"]

    for tenant in active_tenants:
        t_id = tenant["tenant_id"]
        rent = tenant["monthly_rent"]
        
        is_delinquent = random.random() < 0.15 # 15% delinquency rate
        
        # Q3 Payments
        if is_delinquent:
            # Pay random amount or skip a month
            months_paid = random.sample(q3_months, random.choice([1, 2, 3]))
            for m in months_paid:
                amt = rent if random.random() > 0.5 else int(rent * random.uniform(0.3, 0.8))
                date = f"{m}-{str(random.randint(1, 28)).zfill(2)}"
                all_payments.append({"tenant_id": t_id, "date": date, "amount": amt})
        else:
            # Full 3 months
            for m in q3_months:
                date = f"{m}-{str(random.randint(1, 28)).zfill(2)}"
                all_payments.append({"tenant_id": t_id, "date": date, "amount": rent})
        
        # Noise Payments (Outside Q3)
        for m in random.sample(other_months, random.randint(1, 3)):
            date = f"{m}-{str(random.randint(1, 28)).zfill(2)}"
            all_payments.append({"tenant_id": t_id, "date": date, "amount": rent})

    # Shuffle all payments to break chronological order
    random.shuffle(all_payments)

    # Distribute payments into Stripe (JSON), Bank (CSV), Cash (TXT)
    stripe_payments = []
    bank_payments = []
    cash_payments = []

    for p in all_payments:
        dest = random.choice(["stripe", "bank", "cash"])
        if dest == "stripe":
            stripe_payments.append(p)
        elif dest == "bank":
            bank_payments.append(p)
        else:
            cash_payments.append(p)

    # Write Stripe (chunked into 5 JSON files)
    chunk_size = len(stripe_payments) // 5 + 1
    for i in range(5):
        chunk = stripe_payments[i*chunk_size : (i+1)*chunk_size]
        with open(f"payment_gateways/stripe/export_batch_{i}.json", "w") as f:
            json.dump(chunk, f, indent=2)

    # Write Bank (chunked into 4 CSV files)
    chunk_size = len(bank_payments) // 4 + 1
    for i in range(4):
        chunk = bank_payments[i*chunk_size : (i+1)*chunk_size]
        with open(f"payment_gateways/bank/transfer_log_{i}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["TransactionDate", "TenantRef", "AmountReceived", "Currency"])
            for p in chunk:
                writer.writerow([p["date"], p["tenant_id"], p["amount"], "USD"])

    # Write Cash (chunked into 6 TXT logs)
    chunk_size = len(cash_payments) // 6 + 1
    for i in range(6):
        chunk = cash_payments[i*chunk_size : (i+1)*chunk_size]
        with open(f"payment_gateways/cash/drawer_log_{i}.txt", "w") as f:
            f.write(f"--- CASH DRAWER LOG BATCH {i} ---\n")
            for p in chunk:
                f.write(f"TXN - Date: {p['date']} | Tenant: {p['tenant_id']} | Amount: {p['amount']}.00\n")

if __name__ == "__main__":
    build_env()
