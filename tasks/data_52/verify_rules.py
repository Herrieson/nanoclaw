import os
import csv
import json

def verify():
    base_dir = "."
    target_csv = os.path.join(base_dir, "inventory_summary.csv")
    
    state = {
        "csv_exists": False,
        "has_correct_headers": False,
        "data_accuracy": {}
    }

    if not os.path.exists(target_csv):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["csv_exists"] = True

    # Expected values based on the generated deterministic receipts
    # ITEM-101: 3 + 1 + 10 + 2 = 16 sold. Retail: $15.00. Cost: $6.50. Profit per item: $8.50
    # ITEM-202: 1 + 5 + 2 = 8 sold. Retail: $5.50. Cost: $2.00. Profit per item: $3.50
    # ITEM-303: 2 + 4 = 6 sold. Retail: $20.00. Cost: $11.00. Profit per item: $9.00
    
    expected_data = {
        "ITEM-101": {"Total Sold": 16, "Revenue": 240.0, "Profit": 136.0},
        "ITEM-202": {"Total Sold": 8, "Revenue": 44.0, "Profit": 28.0},
        "ITEM-303": {"Total Sold": 6, "Revenue": 120.0, "Profit": 54.0}
    }

    try:
        with open(target_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers == ["Item ID", "Total Sold", "Revenue", "Profit"]:
                state["has_correct_headers"] = True
            
            for row in reader:
                item_id = row.get("Item ID", "").strip()
                if item_id in expected_data:
                    try:
                        sold = int(row.get("Total Sold", 0))
                        revenue = float(row.get("Revenue", 0))
                        profit = float(row.get("Profit", 0))
                        
                        is_correct = (
                            sold == expected_data[item_id]["Total Sold"] and
                            abs(revenue - expected_data[item_id]["Revenue"]) < 0.01 and
                            abs(profit - expected_data[item_id]["Profit"]) < 0.01
                        )
                        state["data_accuracy"][item_id] = is_correct
                    except ValueError:
                        state["data_accuracy"][item_id] = False
    except Exception as e:
        state["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
