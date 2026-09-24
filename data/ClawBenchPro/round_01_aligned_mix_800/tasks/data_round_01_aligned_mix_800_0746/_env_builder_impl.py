import os
import json
import csv

def build_env():
    # Create directory structure
    os.makedirs("raw_inventory", exist_ok=True)
    
    # 1. Warehouse Logs (CSV) - contains some dirty data (negative values, duplicates)
    warehouse_logs = [
        ["timestamp", "item_id", "action", "quantity"],
        ["2023-10-01", "PUMP-001", "OUT", "10"],
        ["2023-10-02", "GEN-500", "OUT", "2"],
        ["2023-10-05", "VALVE-22", "OUT", "50"],
        ["2023-10-05", "VALVE-22", "OUT", "50"], # Duplicate
        ["2023-10-06", "PUMP-001", "OUT", "-5"],  # Dirty data (negative)
        ["2023-10-10", "DRILL-X", "OUT", "5"],
    ]
    with open("raw_inventory/warehouse_shipments.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(warehouse_logs)

    # 2. Official Sales (JSON) - contains item prices and sales records
    sales_data = {
        "quarterly_sales": [
            {"item_id": "PUMP-001", "sold_qty": 10, "unit_price": 1200.0},
            {"item_id": "GEN-500", "sold_qty": 2, "unit_price": 4500.0},
            {"item_id": "VALVE-22", "sold_qty": 100, "unit_price": 45.0},
            {"item_id": "DRILL-X", "sold_qty": 15, "unit_price": 300.0}, # Ghost Stock: 15 sold, but only 5 shipped
            {"item_id": "TRACTOR-09", "sold_qty": 1, "unit_price": 25000.0} # Ghost Stock: 1 sold, 0 shipped
        ]
    }
    with open("raw_inventory/official_sales.json", "w") as f:
        json.dump(sales_data, f, indent=4)

    # 3. Damaged Returns (TXT) - informal notes
    returns_content = """
    Note from Friday:
    Found 2 units of GEN-500 with cracked casings in the return bay. 
    Also, one VALVE-22 was crushed by the forklift. 
    These are write-offs.
    """
    with open("raw_inventory/damaged_notes.txt", "w") as f:
        f.write(returns_content)

if __name__ == "__main__":
    build_env()
