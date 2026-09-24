import os
import json
import re

def verify():
    state = {
        "report_exists": False,
        "shea_butter_650": False,
        "lavender_oil_50": False,
        "rose_water_30": False,
        "rejected_items_excluded": True,
        "distractor_data_excluded": True
    }

    report_dir = "inventory_reports"
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        if files:
            state["report_exists"] = True
            
            combined_text = ""
            for file in files:
                filepath = os.path.join(report_dir, file)
                if os.path.isfile(filepath):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        combined_text += f.read().lower() + "\n"

            if "650" in combined_text and "shea" in combined_text:
                state["shea_butter_650"] = True
            if "50" in combined_text and "lavender" in combined_text:
                state["lavender_oil_50"] = True
            if "30" in combined_text and "rose" in combined_text:
                state["rose_water_30"] = True

            if "lye" in combined_text or "coconut" in combined_text or "dye" in combined_text:
                state["rejected_items_excluded"] = False
                
            if "david" in combined_text or "rachel" in combined_text or "napkin" in combined_text:
                state["distractor_data_excluded"] = False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
