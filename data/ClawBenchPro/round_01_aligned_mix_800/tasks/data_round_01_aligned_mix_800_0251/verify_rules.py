import os
import json
import re

def verify():
    state = {
        "results_dir_exists": False,
        "callback_list_exists": False,
        "supplies_file_exists": False,
        "callback_list_valid_json": False,
        "correct_callback_ids": False,
        "correct_kits_total": False
    }
    
    results_dir = "results"
    callback_file = os.path.join(results_dir, "callback_list.json")
    supplies_file = os.path.join(results_dir, "supplies_needed.txt")
    
    if os.path.isdir(results_dir):
        state["results_dir_exists"] = True
        
    if os.path.isfile(callback_file):
        state["callback_list_exists"] = True
        try:
            with open(callback_file, "r") as f:
                data = json.load(f)
            state["callback_list_valid_json"] = True
            
            # Extract all numbers from the JSON structure
            content_str = json.dumps(data)
            found_ids = set(int(x) for x in re.findall(r'\b10\d\b', content_str))
            
            # Expected IDs from the API backend logic:
            # 102 (Sys >= 140)
            # 103 (Dia >= 90)
            # 104 (Consent == No)
            # 108 (Sys >= 140, Dia >= 90, Consent == No)
            expected_ids = {102, 103, 104, 108}
            
            if found_ids == expected_ids:
                state["correct_callback_ids"] = True
                
        except json.JSONDecodeError:
            pass
            
    if os.path.isfile(supplies_file):
        state["supplies_file_exists"] = True
        try:
            with open(supplies_file, "r") as f:
                content = f.read()
            # Unique patients total kits = 11 or 12 depending on deduplication strategy
            found_nums = set(re.findall(r'\b11\b|\b12\b', content))
            if "11" in found_nums or "12" in found_nums:
                state["correct_kits_total"] = True
        except Exception:
            pass
            
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
