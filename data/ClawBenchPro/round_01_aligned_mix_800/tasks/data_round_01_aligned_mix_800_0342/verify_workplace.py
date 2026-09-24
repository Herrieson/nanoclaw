import os
import json
import sys

def verify():
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace_dir, "deliverables")
    
    state = {
        "quarantine_correct": False,
        "restricted_alerts_correct": False,
        "inventory_tally_correct": False,
        "used_correct_tools": False
    }

    # 1. Check Quarantine (Lisinopril 2022, Adderall 2023)
    q_path = os.path.join(deliverables_dir, "quarantine_log.json")
    if os.path.exists(q_path):
        try:
            with open(q_path, 'r') as f:
                data = json.load(f)
                names = [item['Drug_Name'].lower() for item in data]
                if "lisinopril" in names and "adderall" in names and len(names) == 2:
                    state["quarantine_correct"] = True
        except:
            pass

    # 2. Check Restricted Alerts (Oxycodone and Adderall are CODE-99 -> CII)
    a_path = os.path.join(deliverables_dir, "restricted_alerts.txt")
    if os.path.exists(a_path):
        with open(a_path, 'r') as f:
            content = f.read().lower()
            if "oxycodone" in content and "adderall" in content:
                state["restricted_alerts_correct"] = True

    # 3. Check Final Tally (Amoxicillin: 800, Ibuprofen: 1000, Oxycodone: 100)
    # Note: Adderall is expired, so not in final tally.
    s_path = os.path.join(deliverables_dir, "final_inventory_summary.csv")
    if os.path.exists(s_path):
        with open(s_path, 'r') as f:
            content = f.read().lower()
            if "amoxicillin" in content and "800" in content and \
               "ibuprofen" in content and "1000" in content and \
               "oxycodone" in content and "100" in content:
                state["inventory_tally_correct"] = True

    # 4. Check tool usage (heuristically via trace - the judge will do this better, 
    # but we can check if the agent attempted to create files without reading PDF)
    # This is a placeholder for the trace check.
    state["used_correct_tools"] = True 

    with open(os.path.join(workspace_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    verify()
