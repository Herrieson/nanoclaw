import os
import json

def verify():
    target_file = "workspace/old_market_incidents.json"
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_count": False,
        "correct_content": False
    }
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            if isinstance(data, list) and len(data) == 3:
                state["correct_count"] = True
                
                # Check expected contents loosely
                dates = [item.get("date") for item in data]
                if "1998-04-12" in dates and "1998-04-15" in dates and "1998-04-20" in dates:
                    types = [item.get("incident_type", "").lower() for item in data]
                    if any("vandalism" in t for t in types) and any("intoxication" in t for t in types) and any("burglary" in t for t in types):
                        state["correct_content"] = True
        except Exception:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
