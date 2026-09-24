import os
import json
import csv

def verify():
    state = {
        "audit_folder_exists": False,
        "interlopers_found_correctly": False,
        "emergency_fund_correct": False,
        "summary_report_exists": False
    }
    
    audit_dir = "final_audit"
    if os.path.exists(audit_dir):
        state["audit_folder_exists"] = True
        
        # Check Interlopers
        # Expected: Zoe Saldana, Jack Sparrow
        interlopers_file = None
        for f in os.listdir(audit_dir):
            if "interloper" in f.lower():
                interlopers_file = os.path.join(audit_dir, f)
        
        if interlopers_file:
            with open(interlopers_file, 'r') as f:
                content = f.read()
                if "Zoe Saldana" in content and "Jack Sparrow" in content:
                    state["interlopers_found_correctly"] = True
        
        # Check Summary (Valid count: Alice, Bob, Charlie, Daisy, Fiona = 5; Fund = 190)
        summary_file = None
        for f in os.listdir(audit_dir):
            if "summary" in f.lower() or "report" in f.lower():
                summary_file = os.path.join(audit_dir, f)
        
        if summary_file:
            state["summary_report_exists"] = True
            with open(summary_file, 'r') as f:
                content = f.read()
                # Check for the magic number 190 (Emergency Fund)
                if "190" in content:
                    state["emergency_fund_correct"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
