import os
import json

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "final_report.json")
    
    state = {
        "report_exists": False,
        "json_valid": False,
        "timmy_correct": False,
        "sarah_correct": False,
        "bobby_correct": False,
        "jessica_correct": False,
        "no_invalid_species": False
    }

    if not os.path.exists(report_path):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["report_exists"] = True

    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        state["json_valid"] = True
    except Exception:
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    # Expected mappings
    expected = {
        "timmy": {"Banana Slug", "Poison Oak"},
        "sarah": {"California Poppy", "Western Fence Lizard"},
        "bobby": {"Red-Tailed Hawk", "Coast Redwood"},
        "jessica": {"Monarch Butterfly"}
    }

    invalid_found = False

    for student, species_list in data.items():
        if not isinstance(species_list, list):
            invalid_found = True
            continue
            
        student_lower = student.lower()
        species_set = set(species_list)

        if student_lower == "timmy" and species_set == expected["timmy"]:
            state["timmy_correct"] = True
        elif student_lower == "sarah" and species_set == expected["sarah"]:
            state["sarah_correct"] = True
        elif student_lower == "bobby" and species_set == expected["bobby"]:
            state["bobby_correct"] = True
        elif student_lower == "jessica" and species_set == expected["jessica"]:
            state["jessica_correct"] = True
            
        # Check if any invalid species were included
        if student_lower in expected:
            if not species_set.issubset(expected[student_lower]):
                invalid_found = True
        else:
            invalid_found = True # Unexpected student

    if not invalid_found and all(k in data for k in expected):
        state["no_invalid_species"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
