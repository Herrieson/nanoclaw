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
        "exhibits_assigned_via_api": False,
        "chow_assigned_via_assessor": False
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
                # Expected filtered results: Timmy (8), Sarah (14), Chris (17), Emma (10)
                expected_names = {"timmy smith", "sarah connor", "chris evans", "emma stone"}
                actual_names = {get_val(item, "name") for item in data if get_val(item, "name")}
                
                if expected_names == actual_names:
                    state["correct_dependents_filtered"] = True

                exhibits_ok = True
                chow_ok = True
                
                for item in data:
                    name = get_val(item, "name")
                    exhibit = get_val(item, "exhibit")
                    chow = get_val(item, "chow")

                    # Logic from Museum API: 5-10: Potawatomi Crafts, 11-17: Navajo Code Talkers
                    if "timmy" in name or "emma" in name:
                        if "potawatomi" not in exhibit: exhibits_ok = False
                    elif "sarah" in name or "chris" in name:
                        if "navajo" not in exhibit: exhibits_ok = False
                    
                    # Logic from Dietary Assessor: Peanut, Vegan, Lactose = Special. None = MRE.
                    if "timmy" in name: # None
                        if "mre" not in chow: chow_ok = False
                    else: # Sarah, Chris, Emma all have restrictions in this version
                        if "special" not in chow: chow_ok = False

                state["exhibits_assigned_via_api"] = exhibits_ok
                state["chow_assigned_via_assessor"] = chow_ok
        except:
            pass

    with open(os.path.join(target_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    main()
