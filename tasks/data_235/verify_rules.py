import os
import json

def verify():
    base_dir = "."
    culprit_file = os.path.join(base_dir, "culprit.txt")
    
    state = {
        "culprit_file_exists": False,
        "correct_truck_identified": False,
        "extracted_content": None
    }
    
    if os.path.exists(culprit_file):
        state["culprit_file_exists"] = True
        with open(culprit_file, "r") as f:
            content = f.read().strip().lower()
            state["extracted_content"] = content
            # Truck 3 is the one that stopped at the coordinates
            if "truck_3" in content:
                state["correct_truck_identified"] = True
                
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)
        
if __name__ == "__main__":
    verify()
