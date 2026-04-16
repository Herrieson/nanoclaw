import os
import csv
import json

def verify():
    base_dir = "."
    corrected_ledger_path = os.path.join(base_dir, "corrected_ledger.csv")
    summary_path = os.path.join(base_dir, "summary.txt")
    logs_dir = os.path.join(base_dir, "raw_logs")
    
    state = {
        "corrected_ledger_exists": False,
        "summary_exists": False,
        "ledger_accurate": False,
        "all_tenants_present": False,
        "error_msg": ""
    }
    
    if os.path.exists(summary_path):
        state["summary_exists"] = True
        
    if not os.path.exists(corrected_ledger_path):
        state["error_msg"] = "corrected_ledger.csv not found"
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return
        
    state["corrected_ledger_exists"] = True
    
    # Compute ground truth
    true_totals = {}
    for log_file in os.listdir(logs_dir):
        if log_file.endswith(".txt"):
            with open(os.path.join(logs_dir, log_file), "r") as f:
                lines = f.readlines()[1:]
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    parts = line.split("|")
                    prop, tenant, amount, status = parts[1], parts[2], float(parts[3]), parts[4]
                    key = f"{prop}_{tenant}"
                    if key not in true_totals:
                        true_totals[key] = 0.0
                    if status == "SUCCESS":
                        true_totals[key] += amount
                        
    # Read agent's output
    agent_totals = {}
    try:
        with open(corrected_ledger_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) >= 3:
                    prop, tenant, total = row[0], row[1], float(row[2])
                    agent_totals[f"{prop}_{tenant}"] = total
    except Exception as e:
        state["error_msg"] = f"Error reading ledger: {e}"
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return
        
    if len(agent_totals) == len(true_totals):
        state["all_tenants_present"] = True
        
    # Verify accuracy
    accurate = True
    for key, val in true_totals.items():
        if key not in agent_totals or abs(agent_totals[key] - val) > 0.01:
            accurate = False
            break
            
    if accurate and state["all_tenants_present"]:
        state["ledger_accurate"] = True
    else:
        state["error_msg"] = "Ledger values do not match true SUCCESS totals."
        
    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
