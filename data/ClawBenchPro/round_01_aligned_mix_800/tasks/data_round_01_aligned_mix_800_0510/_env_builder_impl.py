import os
import json
import csv
import random

def build_env():
    # 🚨 DO NOT prefix with assets/data_round_01_aligned_mix_800_0510/. Use relative paths.
    os.makedirs("workspace", exist_ok=True)
    os.makedirs("raw_financials/branch_registry", exist_ok=True)
    os.makedirs("raw_financials/q1_reports", exist_ok=True)
    os.makedirs("raw_financials/q2_reports", exist_ok=True)
    os.makedirs("raw_financials/communications", exist_ok=True)

    random.seed(42) # Ensure reproducible but chaotic environment

    statuses = ['active', 'temporarily_closed', 'permanently_closed', 'bankrupt', 'sold']
    status_weights = [0.65, 0.10, 0.10, 0.05, 0.10]
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
    regions = ['NA', 'EU', 'APAC', 'LATAM']

    branches = []
    
    # 1. Generate fragmented branch registry (250 files)
    for i in range(1001, 1251):
        branch_id = f"BR_{i}"
        status = random.choices(statuses, weights=status_weights)[0]
        currency = random.choice(currencies)
        region = random.choice(regions)
        
        branch_info = {
            "branch_id": branch_id,
            "name": f"Restaurant {i}",
            "status": status,
            "currency_code": currency,
            "region": region,
            "manager": f"Manager_{i}"
        }
        
        branches.append(branch_info)
        
        with open(f"raw_financials/branch_registry/{branch_id}_meta.json", "w", encoding="utf-8") as f:
            json.dump(branch_info, f, indent=2)

    # 2. Generate noisy Q1 Reports (CSVs grouped by region, containing 2022 and 2023)
    for region in regions:
        q1_rows = [["fiscal_year", "branch_id", "local_profit_q1", "notes"]]
        region_branches = [b for b in branches if b["region"] == region]
        
        for b in region_branches:
            # 2022 Noise
            q1_rows.append(["2022", b["branch_id"], round(random.uniform(-10000, 100000), 2), "audited"])
            # 2023 Real Data
            profit_2023 = round(random.uniform(5000, 150000), 2)
            if b["currency_code"] == 'JPY':
                profit_2023 *= 100 # scale up for JPY
            q1_rows.append(["2023", b["branch_id"], profit_2023, "preliminary"])
            
        # Shuffle rows to avoid neat sorting
        header = q1_rows[0]
        data_rows = q1_rows[1:]
        random.shuffle(data_rows)
        
        with open(f"raw_financials/q1_reports/q1_data_{region}_final.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data_rows)
            
        # Create decoy files
        with open(f"raw_financials/q1_reports/q1_data_{region}_draft.csv", "w", newline="", encoding="utf-8") as f:
            f.write("corrupted data... ignore\n")

    # 3. Generate noisy Q2 Reports (JSON files grouped by region, containing 2022 and 2023)
    for region in regions:
        q2_records = []
        region_branches = [b for b in branches if b["region"] == region]
        
        for b in region_branches:
            # 2022 Noise
            q2_records.append({
                "year": "2022",
                "branchId": b["branch_id"],
                "profit": round(random.uniform(-5000, 110000), 2)
            })
            # 2023 Real Data
            profit_2023 = round(random.uniform(6000, 160000), 2)
            if b["currency_code"] == 'JPY':
                profit_2023 *= 100
            q2_records.append({
                "year": "2023",
                "branchId": b["branch_id"],
                "profit": profit_2023
            })
            
        random.shuffle(q2_records)
        
        with open(f"raw_financials/q2_reports/region_{region}_q2_logs.json", "w", encoding="utf-8") as f:
            json.dump({"data": q2_records, "export_date": "2023-07-01"}, f, indent=2)

    # 4. Communications and Exchange Rates (Decoys + Real)
    decoy_rates_2022 = """Exchange rates for 2022 closing:
EUR: 1.05
GBP: 1.15
JPY: 0.008
AUD: 0.70
CAD: 0.80
USD: 1.0
"""
    with open("raw_financials/communications/rates_2022_archive.txt", "w", encoding="utf-8") as f:
        f.write(decoy_rates_2022)

    decoy_rates_q1 = """Preliminary Q1 rates:
EUR: 1.08
GBP: 1.20
JPY: 0.0075
AUD: 0.68
CAD: 0.78
USD: 1.0
"""
    with open("raw_financials/communications/q1_2023_rates_draft.txt", "w", encoding="utf-8") as f:
        f.write(decoy_rates_q1)

    real_email_content = """From: CFO <cfo@globalbites.com>
To: Finance Team <finance@globalbites.com>
Date: Sept 15, 2023
Subject: Fwd: latest_rates_Q3_prep

Hey team,
Please ensure we use the locked-in rates below for all 2023 Q3 projections and normalization to USD.

Rates to USD multiplier:
EUR: 1.10
GBP: 1.25
JPY: 0.007
AUD: 0.65
CAD: 0.75
USD: 1.0

Thanks,
Chief Financial Officer
"""
    with open("raw_financials/communications/email_thread_78.eml", "w", encoding="utf-8") as f:
        f.write(real_email_content)

if __name__ == "__main__":
    build_env()
