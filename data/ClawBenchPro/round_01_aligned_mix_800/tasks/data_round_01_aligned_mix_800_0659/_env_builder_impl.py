import os
import csv
import json

def build_env():
    # 1. Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 2. Generate the messy inventory CSV
    inventory_data = [
        ["Item_ID", "Description", "Department", "Unit_Price", "Quantity"],
        ["101", "Floral Sundress", "Apparel", "25.00", "10"],
        ["102", "Motor Oil 5W-30", "Automotive", "15.00", "5"],   # Misplaced, Value: 75.00
        ["103", "Denim Jacket", "Apparel", "45.00", "8"],
        ["104", "Claw Hammer 16oz", "Hardware", "12.50", "4"],    # Misplaced, Value: 50.00
        ["105", "Silk Scarf", "Apparel", "18.00", "15"],
        ["106", "Spark Plugs (4-pack)", "Automotive", "20.00", "2"], # Misplaced, Value: 40.00
        ["107", "Leather Belt", "Apparel", "22.00", "6"],
        ["108", "Wrench Set", "Hardware", "30.00", "1"],          # Misplaced, Value: 30.00
        ["109", "Canvas Sneakers", "Apparel", "35.00", "12"]
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
