import os
import json
import csv
import random
import string

def build_env():
    # Set a fixed seed for absolute determinism in the environment
    random.seed(1125)

    # 1. Create Directories
    directories = [
        "intel",
        "sys_dumps/account_registry",
        "server_nodes"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 2. Exchange Rates
    rates = {
        "USD": 1.0,
        "EUR": 1.15,
        "GBP": 1.30,
        "JPY": 0.007,
        "CHF": 1.10
    }
    with open("exchange_rates.json", "w") as f:
        json.dump(rates, f, indent=4)

    # 3. Target Profiles (Intel)
    profiles = [
        {"alias": "Viper", "status": "ACTIVE", "threat_level": "HIGH"},
        {"alias": "Oracle", "status": "ACTIVE", "threat_level": "CRITICAL"},
        {"alias": "Ghost", "status": "INACTIVE", "threat_level": "LOW"},
        {"alias": "Cipher", "status": "ACTIVE", "threat_level": "HIGH"},
        {"alias": "Ronin", "status": "INACTIVE", "threat_level": "MEDIUM"}
    ]
    with open("intel/target_profiles.json", "w") as f:
        json.dump(profiles, f, indent=4)

    # 4. Account Registry (Maps Alias to Account ID)
    # Generate 500 fake registry entries
    registry_entries = []
    for i in range(1000, 1500):
        fake_alias = f"Agent_{''.join(random.choices(string.ascii_uppercase, k=4))}"
        registry_entries.append({"alias": fake_alias, "account_id": f"ACC-FAKE-{i}"})
    
    # Inject our targets
    true_mappings = {
        "Viper": "ACC-V-909",
        "Oracle": "ACC-O-111",
        "Ghost": "ACC-G-000",
        "Cipher": "ACC-C-333",
        "Ronin": "ACC-R-777"
    }
    for alias, acc_id in true_mappings.items():
        registry_entries.append({"alias": alias, "account_id": acc_id})
    
    random.shuffle(registry_entries)

    # Distribute registry across 10 files (mixed JSON and CSV)
    for i in range(10):
        chunk = registry_entries[i*50:(i+1)*50]
        if i % 2 == 0:
            with open(f"sys_dumps/account_registry/registry_part_{i}.json", "w") as f:
                json.dump(chunk, f, indent=2)
        else:
            with open(f"sys_dumps/account_registry/registry_part_{i}.csv", "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["alias", "account_id"])
                writer.writeheader()
                writer.writerows(chunk)

    # 5. Generate Transactions
    all_transactions = []
    valid_statuses = ["COMPLETED", "SUCCESS"]
    invalid_statuses = ["PENDING", "FAILED", "REVERTED", "QUARANTINED", "PROCESSING"]
    
    # Generate 5000 noise transactions
    for _ in range(5000):
        dest = f"ACC-NOISE-{random.randint(10000, 99999)}"
        amt = round(random.uniform(10.0, 5000.0), 2)
        ccy = random.choice(list(rates.keys()))
        status = random.choice(valid_statuses + invalid_statuses)
        all_transactions.append((dest, amt, ccy, status))

    # Generate target transactions (including inactive ones as decoys)
    # We want exact totals. We inject enough to ensure robustness.
    target_injections = 300
    for _ in range(target_injections):
        target_acc = random.choice(list(true_mappings.values()))
        amt = round(random.uniform(100.0, 10000.0), 2)
        ccy = random.choice(list(rates.keys()))
        status = random.choice(valid_statuses + invalid_statuses)
        all_transactions.append((target_acc, amt, ccy, status))
        
    random.shuffle(all_transactions)

    # 6. Distribute Transactions across Server Nodes
    # 5 regions, 4 nodes each = 20 nodes
    nodes = []
    for r in range(1, 6):
        for n in range(1, 5):
            node_path = f"server_nodes/region_{r}/node_{n}"
            os.makedirs(node_path, exist_ok=True)
            nodes.append(node_path)
            
    # Split transactions roughly evenly across the 20 nodes
    txs_per_node = len(all_transactions) // len(nodes)
    
    for i, node_path in enumerate(nodes):
        node_txs = all_transactions[i*txs_per_node : (i+1)*txs_per_node]
        
        # Split node_txs into a CSV and a JSON
        mid = len(node_txs) // 2
        csv_txs = node_txs[:mid]
        json_txs = node_txs[mid:]
        
        # Write CSV (Varied headers)
        csv_path = os.path.join(node_path, f"ledger_{i}.csv")
        with open(csv_path, "w", newline='') as f:
            if i % 2 == 0:
                writer = csv.writer(f)
                writer.writerow(["tx_id", "source", "destination", "amount", "currency", "status"])
                for tx in csv_txs:
                    tx_id = f"tx-{random.randint(100000, 999999)}"
                    src = f"ACC-SRC-{random.randint(100, 999)}"
                    writer.writerow([tx_id, src, tx[0], tx[1], tx[2], tx[3]])
            else:
                writer = csv.writer(f)
                writer.writerow(["id", "sender", "beneficiary", "amt", "ccy", "state"])
                for tx in csv_txs:
                    tx_id = f"id-{random.randint(100000, 999999)}"
                    src = f"ACC-SRC-{random.randint(100, 999)}"
                    writer.writerow([tx_id, src, tx[0], tx[1], tx[2], tx[3]])
                    
        # Write JSON (Varied schema)
        json_path = os.path.join(node_path, f"export_{i}.json")
        json_data = []
        if i % 3 == 0:
            for tx in json_txs:
                json_data.append({
                    "tx_ref": f"ref-{random.randint(10000, 99999)}",
                    "from_acc": f"ACC-SRC-{random.randint(100, 999)}",
                    "to_acc": tx[0],
                    "value": tx[1],
                    "coin": tx[2],
                    "tx_status": tx[3]
                })
        else:
             for tx in json_txs:
                json_data.append({
                    "transactionId": f"tr-{random.randint(10000, 99999)}",
                    "origin": f"ACC-SRC-{random.randint(100, 999)}",
                    "target": tx[0],
                    "volume": tx[1],
                    "ticker": tx[2],
                    "condition": tx[3]
                })           
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)

if __name__ == "__main__":
    build_env()
