import os
import json

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "urgent_cases.json")
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_targets": False,
        "found_cases": [],
        "missing_cases": [],
        "extra_cases": []
    }
    
    expected_targets = [
        {"Case ID": "CW-101", "Name": "Emma Watson", "Contact": "555-0101"},
        {"Case ID": "CW-105", "Name": "Sophia Martinez", "Contact": "555-0105"},
        {"Case ID": "CW-106", "Name": "Jackson Lee", "Contact": "555-0106"}
    ]
    
    expected_ids = {t["Case ID"] for t in expected_targets}
    
    if os.path.exists(output_file):
        state["file_exists"] = True
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            if isinstance(data, list):
                found_ids = set()
                for item in data:
                    if isinstance(item, dict) and "Case ID" in item:
                        found_ids.add(item["Case ID"])
                
                state["found_cases"] = list(found_ids)
                state["missing_cases"] = list(expected_ids - found_ids)
                state["extra_cases"] = list(found_ids - expected_ids)
                
                if not state["missing_cases"] and not state["extra_cases"]:
                    # Further check if keys are somewhat correct for the found ones
                    correct_details = True
                    for item in data:
                        if "Name" not in item or "Contact" not in item:
                            correct_details = False
                            break
                    if correct_details:
                        state["correct_targets"] = True
                        
        except json.JSONDecodeError:
            pass
            
    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
