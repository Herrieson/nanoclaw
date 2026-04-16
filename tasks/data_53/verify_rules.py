import os
import json
import re

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "payroll_report.txt")
    
    state = {
        "report_exists": False,
        "alice_hours": None,
        "bob_hours": None,
        "charlie_hours": None,
        "diana_hours": None,
        "evan_hours": None,
        "overtime_alert_correct": False,
        "is_alphabetical": False
    }
    
    if not os.path.exists(report_path):
        with open(os.path.join(base_dir, "state.json"), "w") as f:
            json.dump(state, f)
        return
        
    state["report_exists"] = True
    
    with open(report_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        
    names_in_order = []
    
    for line in lines:
        if line.startswith("Overtime alert:"):
            if "Alice Johnson" in line and not any(n in line for n in ["Bob", "Charlie", "Diana", "Evan"]):
                state["overtime_alert_correct"] = True
            continue
            
        match = re.match(r"(.*?) - (\d+(?:\.\d+)?) hours", line)
        if match:
            name, hours = match.groups()
            hours = float(hours)
            names_in_order.append(name)
            
            if "Alice" in name: state["alice_hours"] = hours
            if "Bob" in name: state["bob_hours"] = hours
            if "Charlie" in name: state["charlie_hours"] = hours
            if "Diana" in name: state["diana_hours"] = hours
            if "Evan" in name: state["evan_hours"] = hours

    if names_in_order == sorted(names_in_order) and len(names_in_order) > 0:
        state["is_alphabetical"] = True
        
    with open(os.path.join(base_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
