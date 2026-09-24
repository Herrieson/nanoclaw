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
            
            # Extract all numbers from the JSON structure to be resilient against formatting
            content_str = json.dumps(data)
            found_ids = set(int(x) for x in re.findall(r'\b10\d\b', content_str))
            
            # The correct IDs needing callback are:
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
            # Calculate total kits used.
            # Unique patients: 101(1), 102(1), 103(1), 104(2), 105(1), 106(1), 107(1), 108(1), 109(2), 110(1)
            # Total = 1+1+1+2+1+1+1+1+2+1 = 12
            # Note: 105 was duplicated with 0 kits in booth 2, and 1 kits in booth 1. 
            # If they keep booth 2's 105, total is 11. If they keep booth 1's 105, total is 12. 
            # Both are acceptable deduplication strategies since prompt says "Just keep their first record, I don't care".
            # 102 is 1 in both.
            found_nums = set(re.findall(r'\b11\b|\b12\b', content))
            if "11" in found_nums or "12" in found_nums:
                state["correct_kits_total"] = True
        except Exception:
            pass
            
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
