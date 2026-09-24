import os
import pandas as pd
import json

def build_env():
    # Create directories
    os.makedirs("raw_records", exist_ok=True)
    os.makedirs("audit_results", exist_ok=True)
    
    # 1. Master Lease List
    master_data = {
        "TenantName": ["John Smith", "Alice Johnson", "Robert Brown", "Emily Davis", "Michael Wilson", "Sarah Miller"],
        "Unit": ["101", "102", "103", "201", "202", "203"],
        "ExpectedMonthlyRent": [1200, 1500, 1100, 1800, 1350, 1600]
    }
    df_master = pd.DataFrame(master_data)
    df_master.to_csv("master_leases.csv", index=False)

    # 2. January (Standard CSV)
    m1 = [
        ["John Smith", 1200], ["Alice Johnson", 1500], ["Robert Brown", 1100], 
        ["Emily Davis", 1800], ["Michael Wilson", 1350], ["Sarah Miller", 1600]
    ]
    pd.DataFrame(m1, columns=["Name", "Amount"]).to_csv("raw_records/payments_january.csv", index=False)

    # 3. February (JSON - Includes Underpayment & Ghost)
    m2 = [
        {"Name": "John Smith", "Paid": 1200},
        {"Name": "Alice Johnson", "Paid": 1500},
        {"Name": "Robert Brown", "Paid": 800}, # Underpaid (Expected 1100)
        {"Name": "Emily Davis", "Paid": 1800},
        {"Name": "Michael Wilson", "Paid": 1350},
        {"Name": "Sarah Miller", "Paid": 1600},
        {"Name": "Unknown Stranger", "Paid": 500} # Ghost
    ]
    with open("raw_records/payments_february.json", "w") as f:
        json.dump(m2, f)

    # 4. March (Mock Image for OCR)
    # The actual content the OCR tool will "return":
    # John Smith: 1200, Alice Johnson: 1500, Robert Brown: 1100, Michael Wilson: 1350, Sarah Miller: 1600, Zodiac Killer: 2000
    # (Emily Davis is missing)
    with open("raw_records/payments_march_scanned.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01") # Fake PNG header

if __name__ == "__main__":
    build_env()
