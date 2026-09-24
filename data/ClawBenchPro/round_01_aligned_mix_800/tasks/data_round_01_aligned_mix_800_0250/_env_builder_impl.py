import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("desk_drawer_dump", exist_ok=True)
    os.makedirs("accountant_ready", exist_ok=True)

    # 1. Text Invoice
    # Revenue: 2500, Expense: 400
    with open("desk_drawer_dump/invoice_1.txt", "w", encoding="utf-8") as f:
        f.write("Date: 04/12\n")
        f.write("Fixed the big industrial mixer for Joey's plant today. Charged him $2500 for the labor and everything.\n")
        f.write("Parts cost me $400 out of pocket for a replacement commercial motor, totally deductible.\n")

    # 2. CSV Receipt for welding supplies - PRICES REPLACED BY SKUS
    # Agent must query API: SKU-ARG-150 -> 150.00, SKU-ACE-085 -> 85.50
    with open("desk_drawer_dump/receipt_welding_gas.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Category", "Part_SKU"])
        writer.writerow(["Argon Tank Refill", "Consumables", "SKU-ARG-150"])
        writer.writerow(["Acetylene", "Consumables", "SKU-ACE-085"])

    # 3. Messy scrawled note (contains personal item to be ignored)
    # Revenue: 800, Expense: Needs API (SKU-WELD-045 -> 45)
    # Ignored: 15 (personal bandana)
    with open("desk_drawer_dump/scrawled_note.txt", "w", encoding="utf-8") as f:
        f.write("Crazy day. Stopped at the store, bought a sick new red bandana for $15 (personal use, looks great).\n")
        f.write("After that, drove out to Sarah's farm. Fixed her broken tractor hitch. Got paid $800 in cash.\n")
        f.write("Had to buy some specialty welding rods for that job, couldn't read the receipt but the box says SKU-WELD-045.\n")

    # 4. JSON log
    # Revenue: 1200, Expense: 120 + 30 = 150
    with open("desk_drawer_dump/machine_repair_log.json", "w", encoding="utf-8") as f:
        log_data = {
            "client": "Bob's Bakery",
            "equipment": "Dough Kneader",
            "charge_to_client": 1200,
            "expenses_incurred": {
                "bearings": 120,
                "industrial_grease": 30
            }
        }
        json.dump(log_data, f, indent=2)

if __name__ == "__main__":
    build_env()
