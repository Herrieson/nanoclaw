import os
import json
import glob

def recursive_search_float(data, target_val, tolerance=0.01):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float)) and abs(v - target_val) < tolerance:
                return True
            if recursive_search_float(v, target_val, tolerance):
                return True
    elif isinstance(data, list):
        for item in data:
            if recursive_search_float(item, target_val, tolerance):
                return True
    return False

def recursive_search_str(data, target_str):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and target_str.lower() in k.lower():
                return True
            if isinstance(v, str) and target_str.lower() in v.lower():
                return True
            if recursive_search_str(v, target_str):
                return True
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and target_str.lower() in item.lower():
                return True
            if recursive_search_str(item, target_str):
                return True
    return False

def verify():
    state = {
        "deliverables_folder_exists": False,
        "json_report_exists": False,
        "valid_json_format": False,
        "correct_approved_hours": False,
        "found_unapproved_gary": False,
        "found_unapproved_melissa": False
    }

    if os.path.exists("deliverables") and os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
        json_files = glob.glob("deliverables/*.json")
        if json_files:
            state["json_report_exists"] = True
            
            for jf in json_files:
                try:
                    with open(jf, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    state["valid_json_format"] = True
                    
                    # Target calculations based on env_builder + skills:
                    # Approved: 
                    # Sarah (4.0) + Chloe (1.5 + 3.5 = 5.0) + Michael (3.5) + Emily (4.0) + David (2.0) = 18.5
                    if recursive_search_float(data, 18.5):
                        state["correct_approved_hours"] = True
                        
                    # Unapproved: Gary Smith, Melissa Vance
                    if recursive_search_str(data, "Gary"):
                        state["found_unapproved_gary"] = True
                    if recursive_search_str(data, "Melissa"):
                        state["found_unapproved_melissa"] = True

                except Exception:
                    pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
