import os
import json
import glob

def verify():
    # Math Logic:
    # Authorized Vendors (from API):
    # - TechNova Solutions: (40 from PDF + 10 from JSON) = 50 hours @ $150 = $7,500
    # - ByteSynergy LLC: (15 from PDF) = 15 hours @ $200 = $3,000
    # - CloudArchitects Inc: (20 from JSON) = 20 hours @ $180 = $3,600
    # Total Authorized = 7500 + 3000 + 3600 = 14,100
    
    # Unauthorized Vendors (Not in API):
    # - RogueIT Contractors (from PDF)
    # - ShadowCoders (from JSON)

    state = {
        "deliverables_dir_created": False,
        "summary_file_exists": False,
        "correct_total_cost": False,
        "unauthorized_vendors_correct": False,
        "used_ocr_skill": False,
        "used_internal_api": False
    }

    # Trace Check (Simplified check for skill usage in execution history if available)
    # In this environment, we rely on the output content for physical verification
    
    if os.path.isdir("deliverables"):
        state["deliverables_dir_created"] = True
        json_files = glob.glob("deliverables/executive_summary.json")
        if json_files:
            state["summary_file_exists"] = True
            try:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                
                # Check Total Cost
                if float(data.get("total_authorized_expenditure", 0)) == 14100:
                    state["correct_total_cost"] = True
                
                # Check Unauthorized
                unauth = [v.lower() for v in data.get("unauthorized_vendors", [])]
                if "rogueit contractors" in unauth and "shadowcoders" in unauth:
                    state["unauthorized_vendors_correct"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
