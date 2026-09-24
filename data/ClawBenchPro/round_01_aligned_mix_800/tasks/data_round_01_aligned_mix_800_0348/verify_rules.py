import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "board_report_exists": False,
        "is_valid_json": False,
        "vetted_hours_correct": False,
        "expenses_correct": False,
        "unvetted_names_identified": False,
        "used_correct_tools": False
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
            
            # Target Data:
            # Cleared: Alice(12.5), Charlie(15.0), Diana(10.0) -> Total 37.5
            # Unvetted: Bob Vance, Evan Wright
            # Total Expenses: 450 + 2500 + 875.5 + 124 = 3949.5
            
            if "37.5" in data_str:
                state["vetted_hours_correct"] = True
                
            if "3949.5" in data_str:
                state["expenses_correct"] = True
                
            if "bob vance" in data_str and "evan wright" in data_str:
                state["unvetted_names_identified"] = True

        except Exception:
            pass

    # Note: Tool usage check is handled by verify_prompt.md via trace analysis
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
