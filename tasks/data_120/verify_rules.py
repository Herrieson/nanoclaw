import os
import json
import sqlite3

def verify():
    results = {
        "script_fixed": False,
        "calculation_correct": False,
        "final_report_exists": False
    }
    
    base_path = "."
    
    # 1. Check if the agent created a summary file or outputted the correct values
    # Correct Math: 
    # Total Area = 1200
    # Walnut = 1200 * 0.6 * 1.15 = 828 board feet
    # Cherry = 1200 * 0.4 * 1.15 = 552 board feet
    # Cost = (828 * 8.50) + (552 * 6.25) = 7038 + 3450 = 10488
    
    # We look for a file named 'summary.json' or 'order_CH-9921.txt' in the workspace
    # Or we can check the agent's last log for these specific numbers.
    # For simplicity in this script, we check a generated report file.
    report_path = os.path.join(base_path, "order_CH-9921_summary.json")
    if os.path.exists(report_path):
        results["final_report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                if abs(data.get("total_cost", 0) - 10488) < 1:
                    results["calculation_correct"] = True
                if data.get("walnut_qty") == 828 and data.get("cherry_qty") == 552:
                    results["quantities_correct"] = True
        except:
            pass
            
    # 2. Check if the script was modified
    script_path = os.path.join(base_path, "scripts/inventory_manager.py")
    with open(script_path, "r") as f:
        content = f.read()
        if "NotImplementedError" not in content:
            results["script_fixed"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
