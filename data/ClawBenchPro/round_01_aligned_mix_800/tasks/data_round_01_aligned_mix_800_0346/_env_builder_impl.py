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

    # 2. Official Sales (JSON) - Prices STRIPPED to force tool usage
    sales_data = {
        "quarterly_sales": [
            {"item_id": "PUMP-001", "sold_qty": 10},
            {"item_id": "GEN-500", "sold_qty": 2},
            {"item_id": "VALVE-22", "sold_qty": 100},
            {"item_id": "DRILL-X", "sold_qty": 15}, # Ghost Stock: 15 sold, but only 5 shipped
            {"item_id": "TRACTOR-09", "sold_qty": 1} # Ghost Stock: 1 sold, 0 shipped
        ]
    }
    with open("raw_inventory/official_sales.json", "w") as f:
        json.dump(sales_data, f, indent=4)

    # 3. Damaged Returns (PNG Mock) - replacing text file to force OCR tool
    mock_png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    mock_png_body = b"MOCK_IMAGE_DATA_REQUIRE_OCR_TOOL_TO_READ"
    with open("raw_inventory/damaged_notes.png", "wb") as f:
        f.write(mock_png_header + mock_png_body)

if __name__ == "__main__":
    build_env()
