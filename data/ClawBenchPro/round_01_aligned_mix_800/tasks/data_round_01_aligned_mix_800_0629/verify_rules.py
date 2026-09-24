import os
import json
import pandas as pd
import glob

def verify():
    report_dir = "archive_report"
    state = {
        "report_folder_exists": os.path.exists(report_dir),
        "consolidated_data_exists": False,
        "summary_exists": False,
        "unique_record_count": 0,
        "total_cost_correct": False,
        "duplicates_identified": False
    }

    # Check for files in the report directory
    files = os.listdir(report_dir) if state["report_folder_exists"] else []
    
    # Looking for a data file (csv or json) and a summary file (txt or md)
    data_files = [f for f in files if f.endswith(('.csv', '.json'))]
    summary_files = [f for f in files if f.endswith(('.txt', '.md', '.json')) and 'summary' in f.lower()]

    if data_files:
        state["consolidated_data_exists"] = True
        try:
            # Expected Unique Valid IDs: ESP-001, ESP-002, ESP-004, ESP-005, ESP-006, ESP-007 (6 total)
            # ESP-003 is invalid (no title), the blank ID in batch 2 is invalid.
            if data_files[0].endswith('.csv'):
                df = pd.read_csv(os.path.join(report_dir, data_files[0]))
                state["unique_record_count"] = len(df)
            elif data_files[0].endswith('.json'):
                with open(os.path.join(report_dir, data_files[0])) as f:
                    data = json.load(f)
                    state["unique_record_count"] = len(data)
        except:
            pass

    if summary_files:
        state["summary_exists"] = True
        content = ""
        with open(os.path.join(report_dir, summary_files[0]), 'r') as f:
            content = f.read()
        
        # Total cost: 6 unique records * 12.50 = 75.0
        if "75" in content:
            state["total_cost_correct"] = True
        
        # Check if they mentioned the duplicates (there were 3 duplicates: 001, 002, 006)
        if "duplicate" in content.lower() or "3" in content:
             state["duplicates_identified"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
