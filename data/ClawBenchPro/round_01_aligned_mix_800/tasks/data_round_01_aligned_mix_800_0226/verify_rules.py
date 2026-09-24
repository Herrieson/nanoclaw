import os
import json

def find_number(d, target):
    if isinstance(d, dict):
        return any(find_number(v, target) for v in d.values())
    elif isinstance(d, list):
        return any(find_number(v, target) for v in d)
    elif isinstance(d, (int, float)):
        return abs(d - target) < 0.01
    return False

def find_list_length(d, target):
    if isinstance(d, dict):
        return any(find_list_length(v, target) for v in d.values())
    elif isinstance(d, list):
        if len(d) == target:
            return True
        return any(find_list_length(v, target) for v in d)
    return False

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "correct_total_bf": False,
        "correct_board_count": False
    }

    report_path = "project_planning/usable_oak_report.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Logic:
            # CSV: 
            # - White Oak 2x6x48 (KN-0) -> Usable. BF: 4
            # - White Oak 2x4x36 (CR-1) -> Usable. BF: 2
            # - White Oak 1x10x60 (RO-9) -> Rejected.
            # PDF:
            # - White Oak 1.5x8x96 (KN-0) -> Usable. BF: 8
            # - White Oak 2x12x72 (SP-5) -> Rejected.
            # - White Oak 1x6x24 (KN-0) -> Usable. BF: 1
            # Total BF: 4 + 2 + 8 + 1 = 15.0
            
            if find_number(data, 15) or find_number(data, 15.0):
                state["correct_total_bf"] = True
                
            if find_list_length(data, 4):
                state["correct_board_count"] = True
                
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
