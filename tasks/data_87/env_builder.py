import os
import json
import csv

def build_env():
    base_dir = "assets/data_87"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy Log File (tokyo_trip_notes_2018.log)
    log_content = """
    Trip Started: 2018-04-12
    Visited Harajuku, had great ramen.
    --- TOKYO ESTATE 2018 PURCHASE LOG ---
    Acquired: ITEM-101 (Condition: Good)
    Skipped the broken lamp.
    Acquired: ITEM-104 (Condition: Excellent, needs slight polish)
    Acquired: ITEM-107 (Condition: Fair)
    Acquired: ITEM-109 (Condition: Mint)
    --- END LOG ---
    Next day: Went to Kyoto. Bought some ceramics (ITEM-201, ITEM-202).
    """
    with open(os.path.join(base_dir, "tokyo_trip_notes_2018.log"), "w") as f:
        f.write(log_content)

    # 2. Warehouse Inventory JSON (wh_inv_final_v2.json)
    inventory = {
        "last_updated": "2023-10-01",
        "items": [
            {"id": "ITEM-101", "location": "Aisle 4", "status": "In Stock"},
            {"id": "ITEM-102", "location": "Aisle 1", "status": "Sold"},
            {"id": "ITEM-104", "location": "Aisle 4", "status": "In Stock"},
            {"id": "ITEM-107", "location": "Aisle 5", "status": "Damaged"},
            {"id": "ITEM-109", "location": "Vault", "status": "In Stock"},
            {"id": "ITEM-201", "location": "Aisle 2", "status": "In Stock"},
            {"id": "ITEM-202", "location": "Aisle 2", "status": "In Stock"}
        ]
    }
    with open(os.path.join(base_dir, "wh_inv_final_v2.json"), "w") as f:
        json.dump(inventory, f, indent=4)

    # 3. Master Prices CSV (prices_master_do_not_edit.csv)
    prices = [
        ["item_id", "item_name", "retail_price"],
        ["ITEM-101", "Noguchi Coffee Table", "2500"],
        ["ITEM-102", "Wegner Wishbone Chair", "800"],
        ["ITEM-104", "Eames Lounge Chair and Ottoman", "6000"],
        ["ITEM-107", "Nakashima Conoid Bench", "12000"],
        ["ITEM-109", "Kofod-Larsen Rosewood Sideboard", "8500"],
        ["ITEM-201", "Mashiko Pottery Vase", "300"],
        ["ITEM-202", "Kutani Tea Set", "450"]
    ]
    with open(os.path.join(base_dir, "prices_master_do_not_edit.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(prices)

if __name__ == "__main__":
    build_env()
