import os
import json
import re

def verify():
    state = {
        "verified_hours_exists": False,
        "luthier_contact_exists": False,
        "json_format_valid": False,
        "correct_aggregation": False,
        "no_unapproved_staff": False,
        "correct_contact_found": False
    }

    hours_file = os.path.join("board_submission", "verified_hours.json")
    contact_file = os.path.join("board_submission", "luthier_contact.txt")

    # Expected values
    expected_hours = {
        "Dr. Adams": 16.0,      # 12 + 4
        "Nurse Sarah": 13.0,    # 8 + 5
        "Dr. Chen": 10.0,       # 10
        "Paramedic Joe": 15.0   # 15
    }
    unapproved_names = ["Fake Volunteer", "Random Guy", "John Doe"]

    # Check hours JSON
    if os.path.exists(hours_file):
        state["verified_hours_exists"] = True
        try:
            with open(hours_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            state["json_format_valid"] = True

            # Normalize keys to string and values to float for robust checking
            parsed_data = {}
            for k, v in data.items():
                parsed_data[str(k).strip()] = float(v)
            
            # Check for correct aggregation
            all_correct = True
            for name, expected_val in expected_hours.items():
                if parsed_data.get(name) != expected_val:
                    all_correct = False
            state["correct_aggregation"] = all_correct

            # Check for unapproved staff
            has_unapproved = False
            for bad_name in unapproved_names:
                if bad_name in parsed_data:
                    has_unapproved = True
            
            # Also check if there are extra keys not in expected_hours
            for k in parsed_data.keys():
                if k not in expected_hours:
                    has_unapproved = True

            state["no_unapproved_staff"] = not has_unapproved

        except Exception:
            pass

    # Check contact file
    if os.path.exists(contact_file):
        state["luthier_contact_exists"] = True
        try:
            with open(contact_file, "r", encoding="utf-8") as f:
                content = f.read()
            # The number in the text is 555-0199-OUD
            if "555-0199" in content:
                state["correct_contact_found"] = True
        except Exception:
            pass

    # Dump state
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
