import os
import json

def verify():
    state = {
        "shift_prep_exists": False,
        "is_valid_json": False,
        "spanish_patients_list_correct": False,
        "dietary_patients_list_correct": False
    }

    target_file = "nursing_station/shift_prep.json"
    
    expected_spanish = {"maria garcia", "carlos perez", "luis rodriguez", "rosa martinez"}
    expected_diet = {"maria garcia", "betty white", "carlos perez", "jane doe", "tom wilson"}

    if os.path.exists(target_file):
        state["shift_prep_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True

            # Helper to find if any list in the JSON matches the expected sets exactly
            def find_matching_list(obj, target_set):
                if isinstance(obj, dict):
                    for val in obj.values():
                        if find_matching_list(val, target_set):
                            return True
                elif isinstance(obj, list):
                    # Check if this list contains strings that exactly match the target set
                    try:
                        current_set = set(str(item).strip().lower() for item in obj)
                        if current_set == target_set:
                            return True
                    except Exception:
                        pass
                    # Also recurse in case it's a list of dicts
                    for item in obj:
                        if find_matching_list(item, target_set):
                            return True
                return False

            if find_matching_list(data, expected_spanish):
                state["spanish_patients_list_correct"] = True
                
            if find_matching_list(data, expected_diet):
                state["dietary_patients_list_correct"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
