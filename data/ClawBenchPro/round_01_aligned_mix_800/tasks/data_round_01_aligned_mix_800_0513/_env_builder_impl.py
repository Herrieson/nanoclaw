import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Set fixed seed for absolute determinism in evaluation
    random.seed(42)

    # 1. Create directory structures
    directories = [
        "configs",
        "compliance/revocations",
        "desk",
        "financial_data/2023/06",
        "financial_data/2023/07",
        "financial_data/2023/08",
        "financial_data/2023/09",
        "financial_data/2023/10",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Build Multi-hop Reference Data: Chart of Accounts
    accounts = {
        "ACC-100": "Corporate",
        "ACC-101": "Corporate",
        "ACC-200": "Private",
        "ACC-201": "Private",
        "ACC-300": "Operating",
        "ACC-301": "PettyCash"
    }
    with open("configs/accounts.json", "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

    # 3. Build Multi-hop Reference Data: Whitelist & Revocations
    base_artists = ["Elena Rostova", "Marcus Vance", "Theodore Lin", "Damien Hirst", "Clara Hughes", "Julian Vance"]
    with open("compliance/base_approved_artists.txt", "w", encoding="utf-8") as f:
        for artist in base_artists:
            f.write(f"{artist}\n")

    revocation_memo = """LEGAL MEMORANDUM
DATE: 2023-05-14
SUBJECT: Vendor Revocations

Due to recent PR issues, the following individuals are hereby permanently revoked from the corporate sponsorship whitelist, effective immediately:
- Damien Hirst
- Clara Hughes

Any further corporate expenditure allocated to these entities will be considered a breach of fiduciary duty.
"""
    with open("compliance/revocations/memo_001_PR_crisis.txt", "w", encoding="utf-8") as f:
        f.write(revocation_memo)

    fake_memo = "Just a reminder that Marcus Vance is doing great work. Keep him on the list."
    with open("compliance/revocations/memo_002_note.txt", "w", encoding="utf-8") as f:
        f.write(fake_memo)

    # 4. Generate highly fragmented transaction logs with noise
    start_date = datetime(2023, 6, 1)
    end_date = datetime(2023, 10, 31)
    
    current_date = start_date
    tx_counter = 1000

    categories = ["Pharma Grant", "Art", "Office Supplies", "Consulting"]
    statuses = ["CLEARED", "CLEARED", "CLEARED", "PENDING", "REVERSED", "FAILED"] # Weighted to Cleared
    recipients = base_artists + ["MediCorp Supplies", "BioSynth Wholesale", "Apex Chemicals", "Banksy", "Staples", "McKinsey"]

    while current_date <= end_date:
        month_str = current_date.strftime("%m")
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Generate 5-15 transactions per day
        daily_txs = []
        num_txs = random.randint(5, 15)
        for _ in range(num_txs):
            tx_id = f"TX-{tx_counter}"
            account_ref = random.choice(list(accounts.keys()))
            expense_type = random.choice(categories)
            
            # Logic tailoring to make sense
            if expense_type == "Pharma Grant":
                recipient = random.choice(["MediCorp Supplies", "BioSynth Wholesale", "Apex Chemicals"])
            elif expense_type == "Art":
                recipient = random.choice(base_artists + ["Banksy"])
            else:
                recipient = random.choice(["Staples", "McKinsey"])

            amount = round(random.uniform(100.0, 150000.0), 2)
            status = random.choice(statuses)

            daily_txs.append({
                "tx_id": tx_id,
                "date": date_str,
                "account_ref": account_ref,
                "expense_type": expense_type,
                "recipient": recipient,
                "amount": amount,
                "tx_state": status
            })
            tx_counter += 1

        # Determine path
        dir_path = f"financial_data/2023/{month_str}"
        file_format = random.choice(["csv", "json"])
        
        if file_format == "csv":
            file_path = os.path.join(dir_path, f"ledger_{date_str}.csv")
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["tx_id", "date", "account_ref", "expense_type", "recipient", "amount", "tx_state"])
                writer.writeheader()
                writer.writerows(daily_txs)
        else:
            file_path = os.path.join(dir_path, f"ledger_{date_str}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"date": date_str, "transactions": daily_txs}, f, indent=4)
                
        current_date += timedelta(days=1)

if __name__ == "__main__":
    build_env()
