import os
import random
import json
import csv

def build_env():
    root = "vault_fragments"
    os.makedirs(root, exist_ok=True)

    # 1. Create a deep, confusing directory structure
    sub_dirs = [
        "archive/2023/ledgers",
        "backups/temp/sys_logs",
        "snapshots/v1/work_in_progress",
        "raw_dumps/recovered_hex",
        "final_reports/legal"
    ]
    for sd in sub_dirs:
        os.makedirs(os.path.join(root, sd), exist_ok=True)

    # 2. Generate NOISE (Thousands of files)
    noise_count = 800
    for i in range(noise_count):
        depth = random.choice(sub_dirs)
        fname = f"log_{random.getrandbits(32)}.txt"
        with open(os.path.join(root, depth, fname), "w") as f:
            f.write(f"Random system noise: {random.random()}\nLine item: Empty\n")

    # 3. Generate DECOYS (Look like sales but are drafts or wrong series)
    decoys = [
        {"Artwork": "Midnight Tears #0", "Buyer": "Ghost", "Price": 99999, "status": "draft"},
        {"Piece": "Crimson Echo #1", "Acquirer": "Real Buyer", "cent_amount": 500000, "status": "settled"},
        {"title": "Midnight Tears #99", "purchaser": "Scammer", "USD": 100, "status": "cancelled"}
    ]
    for i, decoy in enumerate(decoys):
        path = os.path.join(root, "archive/2023/ledgers", f"draft_TX_00{i}.json")
        with open(path, "w") as f:
            json.dump(decoy, f)

    # 4. Generate TRUTH (Fragmented across different formats and folders)
    # Target: "Midnight Tears" series, status: settled/finalized_at
    
    # Fragment A: CSV format in a deep folder
    truth_a = [
        ["item_id", "client_name", "val_usd", "state"],
        ["MT-001", "Alice Liddell", "2500", "settled"],
        ["MT-002", "Bob Miller", "3200", "settled"]
    ]
    with open(os.path.join(root, "raw_dumps/recovered_hex", "TX_88af1_data.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(truth_a)

    # Fragment B: JSON format with different keys
    truth_b = {
        "transaction_id": "TX_9921",
        "records": [
            {"subject": "Midnight Tears #3", "buyer": "Charlie Night", "cent_amount": 450000, "finalized_at": "2023-08-12"},
            {"subject": "Midnight Tears #4", "buyer": "Alice Liddell", "cent_amount": 150000, "finalized_at": "2023-09-01"}
        ]
    }
    with open(os.path.join(root, "snapshots/v1/work_in_progress", "TX_9921_backup.json"), "w") as f:
        json.dump(truth_b, f)

    # Fragment C: Semi-structured TXT format
    truth_c = """
    --- TRANSACTION LOG ---
    REF: TX_CC77
    STATUS: settled
    PIECE: MT-005 (Midnight Tears Series)
    BUYER: Diana Prince
    PRICE: 5000 USD
    -----------------------
    """
    with open(os.path.join(root, "final_reports/legal", "TX_CC77_signed.txt"), "w") as f:
        f.write(truth_c)

if __name__ == "__main__":
    build_env()
