import os
import csv
import random

def build_env():
    os.makedirs("inventory_scans", exist_ok=True)
    
    # Dataset 1: Standard aisle scans
    data1 = [
        ["sku", "product_name", "status", "current_stock", "min_stock"],
        ["SKU-1001", "Cereal Family Pack", "normal", "45", "30"],
        ["SKU-1002", "Paper Towels 12-roll", "normal", "5", "20"], # Needs 15
        ["SKU-1003", "Glass Cleaner", "damaged", "2", "10"],       # Damaged, Needs 8
        ["SKU-1004", "Almond Milk", "normal", "12", "12"],         # Needs 0
    ]
    
    # Dataset 2: Slightly messy data
    data2 = [
        ["sku", "product_name", "status", "current_stock", "min_stock"],
        ["SKU-2001", "Bluetooth Speaker", "normal", "8", "15"],    # Needs 7
        ["SKU-2002", "USB-C Cable", "damaged", "0", "50"],         # Damaged, Needs 50
        ["SKU-2003", "Wireless Mouse", "normal", "22", "10"],      # Needs 0
        ["SKU-2004", "AA Batteries", "missing_tag", "10", "40"],   # Needs 30
    ]

    # Dataset 3: Another aisle
    data3 = [
        ["sku", "product_name", "status", "current_stock", "min_stock"],
        ["SKU-3001", "Yoga Mat", "damaged", "4", "5"],             # Damaged, Needs 1
        ["SKU-3002", "Dumbbells 10lb", "normal", "15", "10"],      # Needs 0
        ["SKU-3003", "Water Bottle", "normal", "2", "20"],         # Needs 18
    ]

    def write_csv(filename, rows):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    write_csv("inventory_scans/aisle_A.csv", data1)
    write_csv("inventory_scans/tech_gadgets_B.csv", data2)
    write_csv("inventory_scans/fitness_C.csv", data3)

if __name__ == "__main__":
    build_env()
