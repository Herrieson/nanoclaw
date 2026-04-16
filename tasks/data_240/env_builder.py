import os
import json
import csv
import shutil

def build_env():
    base_dir = "assets/data_240"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    data_dir = os.path.join(base_dir, "inventory_data")
    sales_dir = os.path.join(data_dir, "sales")
    os.makedirs(sales_dir, exist_ok=True)

    # 1. Warehouse Stock
    warehouse_data = [
        {"SKU": "SF-001", "Title": "Dune", "Genre": "Sci-Fi", "Qty": "15"}, # Limited stock
        {"SKU": "FN-002", "Title": "The Hobbit", "Genre": "Fantasy", "Qty": "100"},
        {"SKU": "SF-003", "Title": "Foundation", "Genre": "Sci-Fi", "Qty": "8"}, # Very limited
        {"SKU": "CK-004", "Title": "Joy of Cooking", "Genre": "Cooking", "Qty": "50"}, # Ignore
        {"SKU": "FN-005", "Title": "Mistborn", "Genre": "Fantasy", "Qty": "50"}
    ]
    with open(os.path.join(data_dir, "warehouse.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["SKU", "Title", "Genre", "Qty"])
        writer.writeheader()
        writer.writerows(warehouse_data)

    # 2. Baseline Store Inventory
    baseline = {
        "Store_A_Alpha": {
            "SF-001": 10,
            "FN-002": 15,
            "SF-003": 5,
            "CK-004": 10,
            "FN-005": 18
        },
        "Store_B_Beta": {
            "SF-001": 12,
            "FN-002": 18,
            "SF-003": 6,
            "CK-004": 5,
            "FN-005": 20
        },
        "Store_C_Gamma": {
            "SF-001": 8,
            "FN-002": 20,
            "SF-003": 2,
            "CK-004": 2,
            "FN-005": 10
        }
    }
    with open(os.path.join(data_dir, "baseline_inventory.json"), "w") as f:
        json.dump(baseline, f, indent=4)

    # 3. Sales Logs
    # Day 1
    with open(os.path.join(sales_dir, "day1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["StoreID", "SKU", "Sold"])
        writer.writerow(["Store_A_Alpha", "SF-001", "3"]) # Current: 7 (Needs 13)
        writer.writerow(["Store_B_Beta", "SF-003", "2"])  # Current: 4 (Needs 16)
        writer.writerow(["Store_C_Gamma", "SF-001", "5"]) # Current: 3 (Needs 17)
        writer.writerow(["Store_A_Alpha", "CK-004", "2"])
    
    # Day 2
    with open(os.path.join(sales_dir, "day2.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["StoreID", "SKU", "Sold"])
        writer.writerow(["Store_B_Beta", "SF-001", "4"])  # Current: 8 (Needs 12)
        writer.writerow(["Store_A_Alpha", "SF-003", "4"]) # Current: 1 (Needs 19)
        writer.writerow(["Store_C_Gamma", "FN-005", "5"]) # Current: 5 (Needs 15)
        writer.writerow(["Store_B_Beta", "FN-002", "3"])  # Current: 15 (Needs 5)

if __name__ == "__main__":
    build_env()
