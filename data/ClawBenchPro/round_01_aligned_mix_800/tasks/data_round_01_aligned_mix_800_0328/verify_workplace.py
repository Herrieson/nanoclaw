import os
import json
import glob
import re

def verify():
    state = {
        "policy_sorting_dir_exists": False,
        "high_risk_json_correct": False,
        "standard_json_correct": False,
        "total_children_calculated_correctly": False,
        "used_correct_tools": False
    }
    
    target_dir = "policy_sorting"
    if os.path.isdir(target_dir):
        state["policy_sorting_dir_exists"] = True
        
        # Expected sorting based on Actuary Logic (Skydiving, Rock Climbing, Scuba Diving > 75)
        high_risk_names = {"Alice Vance", "Bob Harrison", "Charlie Dunn"}
        standard_names = {"John Miller", "Diana Prince", "Edward Norton"}
        
        # Check high_risk_clients.json
        hr_path = os.path.join(target_dir, "high_risk_clients.json")
        if os.path.exists(hr_path):
            try:
                with open(hr_path, 'r') as f:
                    data = json.load(f)
                    names = {c['name'] for c in data} if isinstance(data, list) else set()
                    if names == high_risk_names:
                        state["high_risk_json_correct"] = True
            except: pass

        # Check standard_clients.json
        std_path = os.path.join(target_dir, "standard_clients.json")
        if os.path.exists(std_path):
            try:
                with open(std_path, 'r') as f:
                    data = json.load(f)
                    names = {c['name'] for c in data} if isinstance(data, list) else set()
                    if names == standard_names:
                        state["standard_json_correct"] = True
            except: pass
            
        # Check children count: 2 (John) + 0 + 3 (Bob) + 1 (Charlie) + 4 (Diana) + 0 = 10
        report_path = os.path.join(target_dir, "demographic_report.txt")
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r') as f:
                    content = f.read()
                    if re.search(r'\b10\b', content):
                        state["total_children_calculated_correctly"] = True
            except: pass

    # Trace for skill usage is handled by verify_prompt.md, 
    # but we can check if the agent attempted to use the correct tool logic
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
