import os
import json

def find_number(d, target):
    """Recursively search for a numeric value in parsed JSON."""
    if isinstance(d, dict):
        return any(find_number(v, target) for v in d.values())
    elif isinstance(d, list):
        return any(find_number(v, target) for v in d)
    elif isinstance(d, (int, float)):
        return abs(d - target) < 0.01
    return False

def find_list_length(d, target):
    """Recursively search for a list of a specific length in parsed JSON."""
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
            
            # The total correct board feet should be exactly 15.0
            # Math: (2*6*48/144) + (2*4*36/144) + (1.5*8*96/144) + (1*6*24/144)
            # 4 + 2 + 8 + 1 = 15
            if find_number(data, 15) or find_number(data, 15.0):
                state["correct_total_bf"] = True
                
            # There should be exactly 4 usable White Oak boards
            if find_list_length(data, 4):
                state["correct_board_count"] = True
                
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
