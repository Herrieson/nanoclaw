import os
import pandas as pd
import random

def build_env():
    # Create directories
    os.makedirs("raw_records", exist_ok=True)
    
    # 1. Create Master Lease List
    # Format: TenantName, Unit, ExpectedMonthlyRent
    master_data = {
        "TenantName": ["John Smith", "Alice Johnson", "Robert Brown", "Emily Davis", "Michael Wilson", "Sarah Miller"],
        "Unit": ["101", "102", "103", "201", "202", "203"],
        "ExpectedMonthlyRent": [1200, 1500, 1100, 1800, 1350, 1600]
    }
    df_master = pd.DataFrame(master_data)
    df_master.to_csv("master_leases.csv", index=False)

    # 2. Create Messy Payment Logs (3 months of data)
    # Issues: 
    # - Robert Brown underpaid in Month 2.
    # - "Ghost" payer "Zodiac Killer" (not on lease) paid once.
    # - Emily Davis missed Month 3.
    # - Different formats (some CSV, some JSON)
    
    # Month 1 (Standard CSV)
    m1 = [
        ["John Smith", 1200], ["Alice Johnson", 1500], ["Robert Brown", 1100], 
        ["Emily Davis", 1800], ["Michael Wilson", 1350], ["Sarah Miller", 1600]
    ]
    df_m1 = pd.DataFrame(m1, columns=["Name", "Amount"])
    df_m1.to_csv("raw_records/payments_january.csv", index=False)

    # Month 2 (JSON format, includes an underpayment and a ghost)
    m2 = [
        {"Name": "John Smith", "Paid": 1200},
        {"Name": "Alice Johnson", "Paid": 1500},
        {"Name": "Robert Brown", "Paid": 800}, # Underpayment (Expected 1100)
        {"Name": "Emily Davis", "Paid": 1800},
        {"Name": "Michael Wilson", "Paid": 1350},
        {"Name": "Sarah Miller", "Paid": 1600},
        {"Name": "Unknown Stranger", "Paid": 500} # Ghost payer
    ]
    import json
    with open("raw_records/payments_february.json", "w") as f:
        json.dump(m2, f)

    # Month 3 (Dirty CSV, missing data)
    m3_content = """Name,Amount
John Smith,1200
Alice Johnson,1500
Robert Brown,1100
Michael Wilson,1350
Sarah Miller,1600
# Emily Davis is missing
Zodiac Killer,2000
"""
    with open("raw_records/payments_march.csv", "w") as f:
        f.write(m3_content)

if __name__ == "__main__":
    build_env()
