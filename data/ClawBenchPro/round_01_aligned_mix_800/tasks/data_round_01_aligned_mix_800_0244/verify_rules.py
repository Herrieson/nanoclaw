import os
import json
import glob

def verify():
    state = {
        "deliverables_folder_exists": os.path.isdir("deliverables"),
        "audit_summary_exists": os.path.isfile("deliverables/audit_summary.json"),
        "data_accuracy": False,
        "content": {}
    }
    
    if state["audit_summary_exists"]:
        try:
            with open("deliverables/audit_summary.json", "r") as f:
                data = json.load(f)
                state["content"] = data
                
                # Check metrics
                # Carlos: 001(G), 002(S), 003(G) -> 2 Green, 3 Total
                # Sarah: 004(S), 005(G), 006(G) -> 2 Green, 3 Total
                # Total Green = 4. Ratio = 66.7% for both.
                carlos_green = data.get("reps", {}).get("Carlos", {}).get("green_leases")
                sarah_green = data.get("reps", {}).get("Sarah", {}).get("green_leases")
                
                # Check missing/invalid (CTX-003 is missing, CTX-006 is invalid signature)
                vulnerabilities = data.get("compliance_vulnerabilities", [])
                has_003 = "CTX-003" in vulnerabilities
                has_006 = "CTX-006" in vulnerabilities
                
                if carlos_green == 2 and sarah_green == 2 and has_003 and has_006:
                    state["data_accuracy"] = True
        except:
            pass
                
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
