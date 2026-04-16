import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "sponsor_targets.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_donors_found": False,
        "correct_emails_extracted": False,
        "correct_items_suggested": False,
        "error": None
    }
    
    if not os.path.exists(target_file):
        state["error"] = "sponsor_targets.json not found."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["is_valid_json"] = True
        
        if not isinstance(data, list):
            raise ValueError("Root element must be a list.")
            
        donors = {item.get("name"): item for item in data}
        
        # Check donors (> 500)
        expected_donors = ["Robert Johnson", "Evelyn Montgomery"]
        if set(donors.keys()) == set(expected_donors):
            state["correct_donors_found"] = True
            
        # Check emails
        if donors.get("Robert Johnson", {}).get("email") == "robert.j_donates@montanamail.com" and \
           donors.get("Evelyn Montgomery", {}).get("email") == "evelyn.monty@techgives.org":
            state["correct_emails_extracted"] = True
            
        # Check items
        expected_items = ["Interactive Smart Whiteboard", "Student Tablet 10-inch"]
        robert_items = donors.get("Robert Johnson", {}).get("suggested_items", [])
        evelyn_items = donors.get("Evelyn Montgomery", {}).get("suggested_items", [])
        
        if set(robert_items) == set(expected_items) and set(evelyn_items) == set(expected_items):
             state["correct_items_suggested"] = True

    except Exception as e:
        state["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
