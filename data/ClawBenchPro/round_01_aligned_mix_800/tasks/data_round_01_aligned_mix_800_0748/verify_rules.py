import os
import json
import sys

def verify():
    state = {
        "deliverables_folder_exists": False,
        "board_report_exists": False,
        "is_valid_json": False,
        "vetted_hours_correct": False,
        "expenses_correct": False,
        "unvetted_names_identified": False
    }

    report_path = "deliverables/board_report.json"
    
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
    if os.path.isfile(report_path):
        state["board_report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["is_valid_json"] = True
            
            data_str = json.dumps(data).lower()
            
            # Expected vetted hours: Alice(12.5) + Charlie(15.0) + Diana(10.0) = 37.5
            if "37.5" in data_str:
                state["vetted_hours_correct"] = True
                
            # Expected expenses: 450 + 2500 + 875.5 + 124 = 3949.5
            if "3949.5" in data_str:
                state["expenses_correct"] = True
                
            # Expected unvetted: Bob Vance, Evan Wright
            if "bob vance" in data_str and "evan wright" in data_str:
                state["unvetted_names_identified"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
