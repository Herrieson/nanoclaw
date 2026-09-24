import os
import csv

def build_env():
    # Create the evidence directories
    os.makedirs("evidence/transactions", exist_ok=True)
    
    # Create the suspect list
    suspects = ["ACC-1001-XYZ", "ACC-2002-ABC"]
    with open("evidence/suspects.txt", "w") as f:
        for s in suspects:
            f.write(f"{s}\n")

    # Create Ledger Q1 (Standard format)
    # Target totals: ACC-1001-XYZ: 5400, ACC-2002-ABC: 8000
    data_q1 = [
        ["tx_id", "source_account", "destination_account", "amount_usd", "status"],
        ["tx-8921", "ACC-CORP-99", "ACC-1001-XYZ", "5400.00", "CLEARED"],
        ["tx-8922", "ACC-RETAIL-1", "ACC-9999-FOO", "1200.50", "CLEARED"],
        ["tx-8923", "ACC-HOLDING-2", "ACC-2002-ABC", "8000.00", "CLEARED"],
        ["tx-8924", "ACC-RETAIL-4", "ACC-5555-BAR", "350.00", "PENDING"],
    ]
    with open("evidence/transactions/ledger_Q1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data_q1)

    # Create Ledger Q2 (Slightly messier, different order)
    # Target totals: ACC-1001-XYZ: +1600 (Total: 7000), ACC-2002-ABC: +50 (Total: 8050)
    data_q2 = [
        ["tx_id", "amount_usd", "source_account", "destination_account", "notes"],
        ["tx-9001", "1100.00", "ACC-CORP-88", "ACC-1001-XYZ", "invoice payment"],
        ["tx-9002", "300.00", "ACC-RETAIL-1", "ACC-8888-BAR", "refund"],
        ["tx-9003", "50.00", "ACC-CORP-99", "ACC-2002-ABC", "fee"],
        ["tx-9004", "500.00", "ACC-HOLDING-2", "ACC-1001-XYZ", "consulting"],
    ]
    with open("evidence/transactions/ledger_Q2.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data_q2)

if __name__ == "__main__":
    build_env()
