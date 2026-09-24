import os
import json
import csv

def verify():
    state = {
        "damaged_report_exists": False,
        "damaged_report_valid_json": False,
        "damaged_report_correct_skus": False,
        "restock_summary_exists": False,
        "restock_summary_correct_value": False
    }

    # Verify damaged report
    if os.path.exists("damaged_report.json"):
        state["damaged_report_exists"] = True
        try:
            with open("damaged_report.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            state["damaged_report_valid_json"] = True
            
            # Extract SKUs from whatever structure the agent made
            json_str = json.dumps(data)
            expected_skus = ["SKU-1003", "SKU-2002", "SKU-3001"]
            all_found = all(sku in json_str for sku in expected_skus)
            no_extra = not any(sku in json_str for sku in ["SKU-1001", "SKU-1002", "SKU-1004", "SKU-2001", "SKU-2003", "SKU-2004", "SKU-3002", "SKU-3003"])
            
            if all_found and no_extra:
                state["damaged_report_correct_skus"] = True
        except Exception:
            pass

    # Verify restock summary
    # Calculation: 
    # 1002: 20 - 5 = 15
    # 1003: 10 - 2 = 8
    # 2001: 15 - 8 = 7
    # 2002: 50 - 0 = 50
    # 2004: 40 - 10 = 30
    # 3001: 5 - 4 = 1
    # 3003: 20 - 2 = 18
    # Total = 15 + 8 + 7 + 50 + 30 + 1 + 18 = 129
    
    expected_total = 129
    
    if os.path.exists("restock_summary.txt"):
        state["restock_summary_exists"] = True
        try:
            with open("restock_summary.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
            if str(expected_total) in content:
                state["restock_summary_correct_value"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
