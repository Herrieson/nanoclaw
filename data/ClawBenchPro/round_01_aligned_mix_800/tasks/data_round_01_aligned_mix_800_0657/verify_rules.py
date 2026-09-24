import os
import json
import sys

def get_val(d, key_substring):
    for k, v in d.items():
        if key_substring.lower() in k.lower():
            return str(v).strip().lower()
    return ""

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "deliverables_dir_exists": False,
        "sitrep_exists": False,
        "valid_json": False,
        "correct_dependents_filtered": False,
        "no_invalid_personnel": False,
        "exhibits_assigned_correctly": False,
        "chow_assigned_correctly": False
    }

    deliverables_dir = os.path.join(target_dir, "deliverables")
    sitrep_path = os.path.join(deliverables_dir, "sitrep.json")

    if os.path.exists(deliverables_dir):
        state["deliverables_dir_exists"] = True

    if os.path.exists(sitrep_path):
        state["sitrep_exists"] = True
        try:
            with open(sitrep_path, "r") as f:
                data = json.load(f)
            state["valid_json"] = True

            if isinstance(data, list):
                expected_names = {"timmy smith", "sarah connor", "chris evans", "emma stone"}
                invalid_names = {"john smith", "maya connor", "alex evans", "sgt. major payne"}
                
                actual_names = {get_val(item, "name") for item in data if get_val(item, "name")}
                
                if expected_names.issubset(actual_names) and len(actual_names) == len(expected_names):
                    state["correct_dependents_filtered"] = True
                
                if len(actual_names.intersection(invalid_names)) == 0:
                    state["no_invalid_personnel"] = True

                exhibits_ok = True
                chow_ok = True
                found_targets = 0

                for item in data:
                    name = get_val(item, "name")
                    exhibit = get_val(item, "exhibit")
                    chow = get_val(item, "chow")

                    if not name:
                        continue

                    if "timmy" in name or "emma" in name:
                        found_targets += 1
                        if "potawatomi" not in exhibit:
                            exhibits_ok = False
                        if "mre" not in chow and "standard" not in chow:
                            chow_ok = False
                            
                    elif "sarah" in name or "chris" in name:
                        found_targets += 1
                        if "navajo" not in exhibit and "code" not in exhibit:
                            exhibits_ok = False
                        if "special" not in chow:
                            chow_ok = False

                if found_targets >= 4:
                    state["exhibits_assigned_correctly"] = exhibits_ok
                    state["chow_assigned_correctly"] = chow_ok

        except Exception:
            pass

    with open(os.path.join(target_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    main()
