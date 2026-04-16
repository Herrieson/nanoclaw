import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "operatives.json")
    
    state = {
        "operatives_file_exists": False,
        "is_valid_json": False,
        "extracted_operatives": [],
        "correct_operatives_found": False,
        "no_extra_operatives": False
    }
    
    expected_operatives = {"NIGHTHAWK", "SILVERFOX", "IRONBEAR"}
    wrong_operatives = {"REDBIRD", "BLUEJAY"}
    
    if os.path.exists(target_file):
        state["operatives_file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            if isinstance(data, list):
                extracted = [str(x).upper() for x in data]
                state["extracted_operatives"] = extracted
                
                extracted_set = set(extracted)
                if expected_operatives.issubset(extracted_set):
                    state["correct_operatives_found"] = True
                
                if len(wrong_operatives.intersection(extracted_set)) == 0 and len(extracted_set) == len(expected_operatives):
                    state["no_extra_operatives"] = True
                    
        except Exception as e:
            pass

    score = 0
    if state["operatives_file_exists"]: score += 20
    if state["is_valid_json"]: score += 20
    if state["correct_operatives_found"]: score += 40
    if state["no_extra_operatives"]: score += 20
    
    state["computed_score"] = score

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
