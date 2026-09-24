import os
import json
import sys

def verify():
    state = {
        "deliverables_folder_exists": False,
        "json_file_exists": False,
        "json_format_valid": False,
        "contains_correct_names": False,
        "calculates_correct_hours": False,
        "contains_invalid_names": False
    }
    
    deliverables_dir = "deliverables"
    json_path = os.path.join(deliverables_dir, "ready_volunteers.json")
    
    if os.path.isdir(deliverables_dir):
        state["deliverables_folder_exists"] = True
        
    if os.path.isfile(json_path):
        state["json_file_exists"] = True
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            state["json_format_valid"] = True
            
            data_str = json.dumps(data).lower()
            
            # Correct valid volunteers: Alice Trenton, Diana Prince, Evan Wright, Greg House
            # Total hours: 4 + 3 + 2 + 4 = 13
            # Valid conditions: Age >= 16, Brought an item that is an eco-friendly reusable bottle
            
            # Check names
            has_alice = "alice" in data_str
            has_diana = "diana" in data_str
            has_evan = "evan" in data_str
            has_greg = "greg" in data_str
            
            if has_alice and has_diana and has_evan and has_greg:
                state["contains_correct_names"] = True
                
            # Check invalid names
            has_bobby = "bobby" in data_str  # Age 15
            has_charlie = "charlie" in data_str # Single-use plastic
            has_fiona = "fiona" in data_str # Single-use plastic
            has_hannah = "hannah" in data_str # Age 14
            
            if has_bobby or has_charlie or has_fiona or has_hannah:
                state["contains_invalid_names"] = True
                
            # Check total hours (should be exactly 13)
            def find_value(obj, target):
                if isinstance(obj, dict):
                    return any(find_value(v, target) for v in obj.values())
                elif isinstance(obj, list):
                    return any(find_value(v, target) for v in obj)
                else:
                    return obj == target or str(obj) == str(target)

            if find_value(data, 13) or find_value(data, "13") or find_value(data, 13.0):
                state["calculates_correct_hours"] = True

        except Exception:
            pass

    # Write strict physical state to state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
