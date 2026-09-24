import os
import json
import glob

def verify():
    state = {
        "deliverables_folder_exists": False,
        "json_file_exists": False,
        "json_is_valid": False,
        "math_calculated_perfectly": False,
        "flagged_students_correct": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
        json_files = glob.glob("deliverables/*.json")
        if json_files:
            state["json_file_exists"] = True
            
            # Read the first json file found
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                state["json_is_valid"] = True
                
                # Check Math (Target is 17)
                # Aarav: 3 + 2 = 5
                # Maya: 5
                # Sam: 4
                # Zoe: 3
                # Total = 17
                
                # We do a fuzzy search in the dict values for the number 17
                has_17 = False
                for k, v in data.items():
                    if isinstance(v, (int, float)) and v == 17:
                        has_17 = True
                if has_17:
                    state["math_calculated_perfectly"] = True
                    
                # Check Flagged Students (Leo, Jake, Chloe)
                expected_flagged = {"Leo", "Jake", "Chloe"}
                found_flagged = False
                for k, v in data.items():
                    if isinstance(v, list):
                        # Convert both to sets of strings (ignoring case)
                        val_set = {str(x).strip().lower() for x in v}
                        exp_set = {x.lower() for x in expected_flagged}
                        if exp_set.issubset(val_set) and len(val_set) <= len(exp_set) + 1:
                            found_flagged = True
                if found_flagged:
                    state["flagged_students_correct"] = True
                    
            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
