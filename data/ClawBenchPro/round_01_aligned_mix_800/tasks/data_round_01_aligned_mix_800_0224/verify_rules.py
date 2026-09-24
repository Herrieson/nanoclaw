import os
import json
import glob

def check_results():
    state = {
        "event_prep_exists": False,
        "json_generated": False,
        "correct_headcount_found": False,
        "correct_guests_included": False,
        "artifact_authentication_performed": False, # Checked via trace in verify_prompt
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
                
                # Logic:
                # 1. Alice M.: Confirmed (PDF), Artifact (Verified) -> 1 + 1 Extra = 2
                # 2. David K.: Confirmed (PDF), Artifact (Verified) -> 1 + 0 Extra = 1
                # 3. Charlie: Confirmed (PDF), Artifact (Verified) -> 1 + 2 Extras = 3
                # 4. Frank: Confirmed (PDF), Artifact (FAILED Auth) -> 0
                # 5. Eve: Pending (PDF) -> 0
                # Total Headcount = 2 + 1 + 3 = 6
                
                if "6" in content_str:
                    state["correct_headcount_found"] = True
                
                # Alice, David, and Charlie should be there. 
                # Frank (Failed Auth), Bob (Declined), Eve (Pending) should not.
                if all(name in content_str for name in ["alice m", "david k", "charlie"]):
                    state["correct_guests_included"] = True
                    
                wrong_names = ["frank", "bob", "eve"]
                if any(name in content_str for name in wrong_names):
                    state["wrong_guests_excluded"] = False
                    
            except Exception:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    check_results()
