import os
import json
import csv

def build_env():
    base_dir = "assets/data_414"
    records_dir = os.path.join(base_dir, "records")
    
    os.makedirs(os.path.join(records_dir, "jan"), exist_ok=True)
    os.makedirs(os.path.join(records_dir, "feb"), exist_ok=True)
    os.makedirs(os.path.join(records_dir, "mar"), exist_ok=True)
    os.makedirs(os.path.join(records_dir, "notes"), exist_ok=True)

    # 1. Ledger Summary
    ledger_content = """Q1 2023 Official Ledger Summary
-------------------------------
Travel: 1540.00
Meals: 320.50
Office Supplies: 400.00
Software Subscriptions: 890.99
Miscellaneous: 150.00
"""
    with open(os.path.join(base_dir, "ledger_summary.txt"), "w", encoding="utf-8") as f:
        f.write(ledger_content)

    # 2. Jan CSV
    jan_csv_path = os.path.join(records_dir, "jan", "expenses_01.csv")
    with open(jan_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Amount", "Status"])
        writer.writerow(["2023-01-05", "Meals", "45.00", "Cleared"])
        writer.writerow(["2023-01-12", "Office Supplies", "100.50", "Cleared"]) # +100.50
        writer.writerow(["2023-01-15", "Travel", "300.00", "Cleared"])
        writer.writerow(["2023-01-22", "Suministros de Oficina", "45.20", "Cleared"]) # +45.20

    # 3. Feb JSON
    feb_json_path = os.path.join(records_dir, "feb", "data_02.json")
    feb_data = [
        {"date": "2023-02-01", "type": "Software", "cost": 45.99},
        {"date": "2023-02-10", "type": "Office Supplies", "cost": 200.00}, # +200.00
        {"date": "2023-02-14", "type": "Meals", "cost": 85.00},
        {"date": "2023-02-28", "type": "Office Supplies", "cost": -50.00}  # -50.00 (Refund)
    ]
    with open(feb_json_path, "w", encoding="utf-8") as f:
        json.dump(feb_data, f, indent=4)

    # 4. Mar TXT (Unstructured)
    mar_txt_path = os.path.join(records_dir, "mar", "rough_notes.txt")
    mar_notes = """March Expenses Rough Log
------------------------
03/02 - Client dinner. Meals: $120.00
03/08 - Suministros de Oficina: $35.50 (Need to keep receipt)
03/15 - Flight to NY. Travel: $450.00
03/22 - Bought printer ink and paper. Office Supplies: $120.00
03/30 - Suministros de Oficina refund for damaged paper: -$10.00
"""
    # Totals: 35.50 + 120.00 - 10.00
    with open(mar_txt_path, "w", encoding="utf-8") as f:
        f.write(mar_notes)

    # 5. Extra noise file
    misc_path = os.path.join(records_dir, "notes", "misc.json")
    misc_data = {"personal_yoga": 50.00, "gardening_tools": 150.00}
    with open(misc_path, "w", encoding="utf-8") as f:
        json.dump(misc_data, f)

    # Target calculation:
    # 100.50 + 45.20 + 200.00 - 50.00 + 35.50 + 120.00 - 10.00 = 441.20
    # Ledger: 400.00
    # Discrepancy: 41.20

if __name__ == "__main__":
    build_env()
