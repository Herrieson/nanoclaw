import os
import csv
import json

def build_env():
    # 1. Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 2. Generate the stripped-down inventory CSV (Department and Unit_Price removed)
    inventory_data = [
        ["Item_ID", "SKU_Code", "Quantity"],
        ["101", "SKU-FLR-01", "10"],
        ["102", "SKU-OIL-5W", "5"],   # Misplaced, Auto
        ["103", "SKU-DNM-JK", "8"],
        ["104", "SKU-CWH-16", "4"],   # Misplaced, Hardware
        ["105", "SKU-SLK-SF", "15"],
        ["106", "SKU-SPK-P4", "2"],   # Misplaced, Auto
        ["107", "SKU-LTH-BT", "6"],
        ["108", "SKU-WRN-ST", "1"],   # Misplaced, Hardware
        ["109", "SKU-CVS-SN", "12"]
    ]
    
    with open("data/inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(inventory_data)

    # 3. Generate the weekend schedule JSON
    schedule_data = {
        "Sarah": {"Saturday": 4, "Sunday": 3},
        "Mike": {"Saturday": 5, "Sunday": 4},      # Overtime (9 hours)
        "Jessica": {"Saturday": 8, "Sunday": 0},
        "David": {"Saturday": 6, "Sunday": 6},     # Overtime (12 hours)
        "Emily": {"Saturday": 0, "Sunday": 5},
        "Tom": {"Saturday": 4.5, "Sunday": 4.5}    # Overtime (9 hours)
    }

    with open("data/weekend_shifts.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, indent=4)

if __name__ == "__main__":
    build_env()
