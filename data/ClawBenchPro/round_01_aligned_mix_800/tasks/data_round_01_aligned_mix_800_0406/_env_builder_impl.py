import os
import json
import csv
import random

def build_env():
    # Set seed for deterministic chaos
    random.seed(1267)

    # 1. Directories
    os.makedirs("deliverables", exist_ok=True)
    base_archives = "pta_data_dump/archives"
    os.makedirs(base_archives, exist_ok=True)
    os.makedirs("pta_data_dump/front_desk", exist_ok=True)
    os.makedirs("pta_data_dump/system_exports", exist_ok=True)

    # 2. Generate Parents
    first_names = ["Sarah", "John", "Alice", "Marcus", "Beatrice", "Tom", "Eleanor", "Nancy", "Mike", "Chloe", "David", "Emma", "Frank", "Grace"]
    last_names = ["Connor", "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson"]
    parents = {}
    for i in range(1, 151):
        pid = f"P{i:03d}"
        parents[pid] = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    with open("pta_data_dump/system_exports/parent_directory.json", "w", encoding="utf-8") as f:
        # Save as array of dicts to require simple parsing
        json.dump([{"parent_id": pid, "full_name": name} for pid, name in parents.items()], f, indent=2)

    # 3. Generate Transactions
    campaigns = ["St. Jude's Book & Bake", "Spring Dance", "Pizza Fundraiser", "Winter Gala"]
    item_types = ["ChildrensBook", "AdultBook", "BakedGood", "PizzaSlice", "DanceTicket", "SoftDrink"]

    all_txns = []
    voided_txns = set()

    for t_id in range(1, 801):
        txn_id = f"TXN{t_id:04d}"
        pid = random.choice(list(parents.keys()))
        campaign = random.choices(campaigns, weights=[0.6, 0.2, 0.1, 0.1])[0]
        
        # Decide items based on campaign to make it somewhat realistic
        items = []
        if campaign == "St. Jude's Book & Bake":
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                items.append({
                    "type": random.choice(["ChildrensBook", "AdultBook", "BakedGood"]),
                    "qty": random.randint(1, 5)
                })
        else:
            num_items = random.randint(1, 2)
            for _ in range(num_items):
                items.append({
                    "type": random.choice(["PizzaSlice", "DanceTicket", "SoftDrink"]),
                    "qty": random.randint(1, 10)
                })
        
        all_txns.append({
            "txn_id": txn_id,
            "parent_id": pid,
            "campaign": campaign,
            "items": items
        })

        # 15% chance to be voided
        if random.random() < 0.15:
            voided_txns.add(txn_id)

    # 4. Save Voided Transactions
    with open("pta_data_dump/front_desk/cancellations.txt", "w", encoding="utf-8") as f:
        f.write("--- CANCELLATION LOG ---\n")
        f.write("Do not process the following transactions:\n")
        for vt in voided_txns:
            f.write(f"{vt}\n")

    # 5. Scatter Transactions in Archives (JSON and CSV mix)
    for i, txn in enumerate(all_txns):
        # Create random nested folders
        year_folder = f"year_{random.choice(['2021', '2022', '2023'])}"
        month_folder = f"month_{random.randint(1, 12):02d}"
        dir_path = os.path.join(base_archives, year_folder, month_folder)
        os.makedirs(dir_path, exist_ok=True)

        if random.random() < 0.5:
            # Save as JSON
            filepath = os.path.join(dir_path, f"{txn['txn_id']}_log.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(txn, f)
        else:
            # Save as CSV (flattened)
            filepath = os.path.join(dir_path, f"{txn['txn_id']}_log.csv")
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["txn_id", "parent_id", "campaign", "item_type", "qty"])
                for itm in txn["items"]:
                    writer.writerow([txn["txn_id"], txn["parent_id"], txn["campaign"], itm["type"], itm["qty"]])
                    
    # Add some dummy noise files
    for _ in range(20):
        dummy_dir = os.path.join(base_archives, "unknown_dumps")
        os.makedirs(dummy_dir, exist_ok=True)
        with open(os.path.join(dummy_dir, f"junk_{random.randint(100,999)}.txt"), "w") as f:
            f.write("Corrupted data. Do not use.")

if __name__ == "__main__":
    build_env()
