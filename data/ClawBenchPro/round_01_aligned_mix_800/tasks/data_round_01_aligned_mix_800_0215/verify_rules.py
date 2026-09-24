import os
import json
import glob

def find_in_json(obj, target_val):
    """Recursively search for a value in a parsed JSON object."""
    if isinstance(obj, dict):
        for v in obj.values():
            if find_in_json(v, target_val): 
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find_in_json(item, target_val): 
                return True
    else:
        # Check numeric equivalence
        if isinstance(obj, (int, float)) and isinstance(target_val, (int, float)):
            if abs(obj - target_val) < 0.001: 
                return True
        # Check string inclusion
        if isinstance(obj, str) and isinstance(target_val, str):
            if target_val.lower() in obj.lower(): 
                return True
    return False

def verify():
    state = {
        "deliverables_folder_has_json": False,
        "json_is_valid": False,
        "total_legitimate_cost_correct": False,
        "unapproved_contractor_shady_steve_found": False,
        "unapproved_contractor_mikes_lawn_care_found": False,
        "unapproved_contractor_quickfix_llc_found": False
    }

    # True legitimate total should be:
    # A1 Plumbing: 150.00 + 75.25 = 225.25
    # Holy Cross Roofers: 500.00 + 1200.00 = 1700.00
    # St. Peter Landscaping: 350.50
    # Total = 2275.75

    json_files = glob.glob("deliverables/*.json")
    
    if json_files:
        state["deliverables_folder_has_json"] = True
        
        for jf in json_files:
            try:
                with open(jf, "r") as f:
                    data = json.load(f)
                
                state["json_is_valid"] = True
                
                # Check target numerical sum
                if find_in_json(data, 2275.75):
                    state["total_legitimate_cost_correct"] = True
                
                # Check unapproved contractors
                if find_in_json(data, "Shady Steve"):
                    state["unapproved_contractor_shady_steve_found"] = True
                if find_in_json(data, "Mike's Lawn Care") or find_in_json(data, "Mikes Lawn Care"):
                    state["unapproved_contractor_mikes_lawn_care_found"] = True
                if find_in_json(data, "QuickFix LLC") or find_in_json(data, "QuickFix"):
                    state["unapproved_contractor_quickfix_llc_found"] = True

            except Exception:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
