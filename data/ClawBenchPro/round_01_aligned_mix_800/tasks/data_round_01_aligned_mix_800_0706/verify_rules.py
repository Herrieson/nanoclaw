import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "has_output_file": False,
        "correct_hours_found": False,
        "invasive_names_excluded": False,
        "invasive_plants_excluded": False,
        "approved_names_included": False
    }
    
    deliv_dir = "garden_deliverables"
    if os.path.isdir(deliv_dir):
        state["deliverables_folder_exists"] = True
        
        files = os.listdir(deliv_dir)
        if len(files) > 0:
            state["has_output_file"] = True
            
            combined_text = ""
            for fname in files:
                filepath = os.path.join(deliv_dir, fname)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            combined_text += f.read().lower() + "\n"
                    except:
                        pass
            
            # The correct total hours for non-invasive (Alice 5, Charlie 3, Eve 4, Grace 2) is 14.
            if "14" in combined_text:
                state["correct_hours_found"] = True
                
            # Check exclusion of invasive requesters (Bob, David, Frank)
            if not any(bad_name in combined_text for bad_name in ["bob", "david", "frank"]):
                state["invasive_names_excluded"] = True
                
            # Check exclusion of invasive plants
            if not any(bad_plant in combined_text for bad_plant in ["english ivy", "kudzu", "japanese knotweed", "knotweed"]):
                state["invasive_plants_excluded"] = True
                
            # Check inclusion of approved names
            if all(good_name in combined_text for good_name in ["alice", "charlie", "eve", "grace"]):
                state["approved_names_included"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
