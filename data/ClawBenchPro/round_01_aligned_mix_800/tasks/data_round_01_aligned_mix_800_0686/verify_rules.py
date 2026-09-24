import os
import json
import sys

def verify():
    state = {
        "showcase_prep_exists": False,
        "uncleared_volunteers_file_exists": False,
        "consultation_file_exists": False,
        "uncleared_volunteers_correct": False,
        "consultations_correct": False
    }

    if os.path.isdir("showcase_prep"):
        state["showcase_prep_exists"] = True

        files_in_prep = os.listdir("showcase_prep")
        
        # Try to find the files based on content or reasonable naming
        uncleared_file = None
        consultation_file = None
        
        for fname in files_in_prep:
            if not fname.endswith('.json'): continue
            path = os.path.join("showcase_prep", fname)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    
                    # Convert data to string for rough heuristics
                    data_str = str(data).lower()
                    
                    if "bob" in data_str and "builder" in data_str:
                        uncleared_file = path
                        state["uncleared_volunteers_file_exists"] = True
                    
                    if "mia" in data_str and "david" in data_str:
                        consultation_file = path
                        state["consultation_file_exists"] = True
            except:
                pass

        # Exact check for Uncleared Volunteers
        if uncleared_file:
            try:
                with open(uncleared_file, "r") as f:
                    v_data = json.load(f)
                    flat_v = str(v_data)
                    if "Bob Builder" in flat_v and "Karen Smith" in flat_v and "Maria Silva" not in flat_v:
                        state["uncleared_volunteers_correct"] = True
            except:
                pass

        # Exact check for Consultations
        if consultation_file:
            try:
                with open(consultation_file, "r") as f:
                    c_data = json.load(f)
                    flat_c = str(c_data)
                    if "Mia" in flat_c and "David" in flat_c and "Omar" in flat_c and "Leo" not in flat_c:
                        state["consultations_correct"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
