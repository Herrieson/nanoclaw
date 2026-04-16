import os
import csv
import random

def build_env():
    base_dir = "assets/data_93"
    os.makedirs(os.path.join(base_dir, "raw_logs"), exist_ok=True)
    
    properties = ["Oakwood Apartments", "Maple Ridge", "Pine Crest"]
    tenants = {
        "Oakwood Apartments": ["Alice Smith", "Bob Jones", "Charlie Brown"],
        "Maple Ridge": ["David Wilson", "Eva Davis"],
        "Pine Crest": ["Frank Miller", "Grace Lee"]
    }
    
    transactions = []
    txn_id = 1000
    
    # Generate deterministic but chaotic looking transactions
    random.seed(42) 
    
    for prop in properties:
        for tenant in tenants[prop]:
            # Generate 1 to 3 successful transactions
            for _ in range(random.randint(1, 3)):
                transactions.append(f"TXN_{txn_id}|{prop}|{tenant}|1500.00|SUCCESS")
                txn_id += 1
            # Generate 1 pending transaction
            transactions.append(f"TXN_{txn_id}|{prop}|{tenant}|1500.00|PENDING")
            txn_id += 1
            # Generate 1 failed transaction
            transactions.append(f"TXN_{txn_id}|{prop}|{tenant}|1500.00|FAILED")
            txn_id += 1
            
    random.shuffle(transactions)
    
    # Split into 3 log files to simulate daily logs
    chunk_size = len(transactions) // 3 + 1
    for i in range(3):
        with open(os.path.join(base_dir, "raw_logs", f"log_day_{i+1}.txt"), "w") as f:
            f.write("TXN_ID|PROPERTY|TENANT|AMOUNT|STATUS\n")
            for txn in transactions[i*chunk_size : (i+1)*chunk_size]:
                f.write(txn + "\n")
                
    # Generate original buggy ledger
    with open(os.path.join(base_dir, "ledger.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Property", "Tenant", "Total_Paid"])
        for prop in properties:
            for tenant in tenants[prop]:
                amount = 0.0
                # Bug implementation matching the prompt's complaint
                if prop == "Maple Ridge":
                    amount = 0.0
                else:
                    for txn in transactions:
                        parts = txn.split("|")
                        if parts[1] == prop and parts[2] == tenant:
                            if prop == "Oakwood Apartments":
                                if parts[4] == "SUCCESS":
                                    amount += float(parts[3])
                                elif parts[4] == "PENDING":
                                    amount += float(parts[3]) * 2
                            else:
                                if parts[4] == "SUCCESS":
                                    amount += float(parts[3])
                writer.writerow([prop, tenant, f"{amount:.2f}"])

if __name__ == "__main__":
    build_env()
