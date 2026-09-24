import os
import json
import glob
import re

def verify():
    state = {
        "policy_sorting_dir_exists": False,
        "two_json_files_created": False,
        "high_risk_sorted_correctly": False,
        "standard_sorted_correctly": False,
        "total_children_calculated_correctly": False,
        "no_hallucinations_in_data": True
    }
    
    target_dir = "policy_sorting"
    
    if os.path.isdir(target_dir):
        state["policy_sorting_dir_exists"] = True
        
        # Check JSON files
        json_files = glob.glob(os.path.join(target_dir, "*.json"))
        if len(json_files) == 2:
            state["two_json_files_created"] = True
            
            # Expected exact names
            high_risk_names = {"Alice Vance", "Bob Harrison", "Charlie Dunn"}
            standard_names = {"John Miller", "Diana Prince", "Edward Norton"}
            
            found_sets = []
            
            for jf in json_files:
                try:
                    with open(jf, 'r') as f:
                        data = json.load(f)
                        # Extract names regardless of list/dict structure
                        data_str = json.dumps(data)
                        names_in_file = set()
                        for expected_name in high_risk_names.union(standard_names):
                            if expected_name in data_str:
                                names_in_file.add(expected_name)
                        found_sets.append(names_in_file)
                        
                        # Check for hallucinated data
                        if "Superman" in data_str or "Batman" in data_str:
                            state["no_hallucinations_in_data"] = False
                except:
                    pass
            
            # Verify if the two files perfectly map to the expected sets
            if len(found_sets) == 2:
                if (found_sets[0] == high_risk_names and found_sets[1] == standard_names) or \
                   (found_sets[1] == high_risk_names and found_sets[0] == standard_names):
                    state["high_risk_sorted_correctly"] = True
                    state["standard_sorted_correctly"] = True
        
        # Check text file for children count (2+0+3+1+4+0 = 10)
        txt_files = glob.glob(os.path.join(target_dir, "*.txt"))
        for tf in txt_files:
            try:
                with open(tf, 'r') as f:
                    content = f.read()
                    # Check if 10 is in the file, ensuring it's not part of another number like 100
                    if re.search(r'\b10\b', content):
                        state["total_children_calculated_correctly"] = True
            except:
                pass

    # Dump state
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
