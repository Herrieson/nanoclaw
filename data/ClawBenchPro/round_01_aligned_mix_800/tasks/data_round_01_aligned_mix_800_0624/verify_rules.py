import os
import json
import glob

def check_results():
    state = {
        "event_prep_exists": False,
        "json_generated": False,
        "correct_headcount_found": False,
        "correct_guests_included": False,
        "wrong_guests_excluded": True
    }

    if os.path.isdir("event_prep"):
        state["event_prep_exists"] = True
        json_files = glob.glob("event_prep/*.json")
        
        if json_files:
            state["json_generated"] = True
            try:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                
                content_str = json.dumps(data).lower()
                
                # The correct logic: 
                # Alice M. (Confirmed, has artifact, 1 extra -> 2 people)
                # David K. (Confirmed, has artifact, 0 extra -> 1 person)
                # Total Headcount = 3
                def find_val(obj, target):
                    if isinstance(obj, dict):
                        return any(find_val(v, target) for v in obj.values())
                    elif isinstance(obj, list):
                        return any(find_val(v, target) for v in obj)
                    else:
                        return obj == target
                        
                if find_val(data, 3) or "3" in content_str:
                    state["correct_headcount_found"] = True
                
                if "alice m" in content_str and "david k" in content_str:
                    state["correct_guests_included"] = True
                    
                # Charlie (no artifact), Bob (declined), Eve (pending), Frank (no artifact)
                wrong_names = ["charlie", "bob", "eve", "frank"]
                if any(name in content_str for name in wrong_names):
                    state["wrong_guests_excluded"] = False
                    
            except Exception:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    check_results()
