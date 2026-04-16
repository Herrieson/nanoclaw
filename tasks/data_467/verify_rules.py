import os
import pandas as pd
import json

def verify():
    results = {
        "po_hash_correct": False,
        "total_amount_correct": False,
        "csv_generated": False,
        "csv_content_correct": False
    }
    
    # 1. Check if the Agent found the PO Hash and Amount (this usually comes from the final response, 
    # but we can check if they created a summary file or log)
    # For this task, we expect the Agent to output the answer. 
    # Let's check for the required CSV file.
    csv_path = "low-stock-report.csv"
    if os.path.exists(csv_path):
        results["csv_generated"] = True
        try:
            df = pd.read_csv(csv_path)
            # Low stock items: Desert Trinkets (12), Grand Canyon Mugs (8)
            expected_names = {"Desert Trinkets", "Grand Canyon Mugs"}
            actual_names = set(df['name'].tolist())
            if expected_names == actual_names:
                results["csv_content_correct"] = True
        except:
            pass

    # Note: PO Hash and Amount will be verified by the LLM Judge from the trace.
    # We output the state for the judge.
    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
