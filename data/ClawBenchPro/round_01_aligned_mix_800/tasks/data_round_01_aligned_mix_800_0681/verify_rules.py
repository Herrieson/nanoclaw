import os
import json
import csv

def verify():
    state = {
        "reports_dir_exists": False,
        "discrepancy_report_exists": False,
        "low_stock_report_exists": False,
        "total_overcharge_correct": False,
        "low_stock_count_correct": False,
        "found_cleancorp_overcharges": False
    }

    report_path = "reports/Discrepancy_Report.txt" # Flexible naming allowed but checked
    # Check for any file in reports/ that looks like a discrepancy report
    if os.path.exists("reports"):
        state["reports_dir_exists"] = True
        files = os.listdir("reports")
        
        disc_file = next((f for f in files if "discrepancy" in f.lower()), None)
        low_stock_file = next((f for f in files if "low" in f.lower() and "stock" in f.lower()), None)
        
        if disc_file:
            state["discrepancy_report_exists"] = True
            with open(f"reports/{disc_file}", "r") as f:
                content = f.read()
                # Expected overcharge is 14.00
                if "14.00" in content or "14.0" in content:
                    state["total_overcharge_correct"] = True
                if "CleanCorp" in content:
                    state["found_cleancorp_overcharges"] = True
        
        if low_stock_file:
            state["low_stock_report_exists"] = True
            with open(f"reports/{low_stock_file}", "r") as f:
                content = f.read().lower()
                # Low stock items: WAX_002 (3), SOAP_005 (1), BRUSH_004 (3). MOP_003 is exactly 5 (not less than 5).
                # Wait, prompt said "less than 5". So MOP_003 (5) is NOT low stock.
                # Items: WAX_002, SOAP_005, BRUSH_004.
                if "wax_002" in content and "soap_005" in content and "brush_004" in content:
                    if "mop_003" not in content:
                        state["low_stock_count_correct"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
