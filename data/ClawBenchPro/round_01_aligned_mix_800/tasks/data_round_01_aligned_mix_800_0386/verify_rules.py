import os
import json
import re

def verify():
    state = {
        "planning_dir_exists": False,
        "equipment_file_exists": False,
        "hours_file_exists": False,
        "found_john": False,
        "found_dave": False,
        "found_sarah": False,
        "excluded_bob": False,
        "excluded_carl": False,
        "total_hours_correct": False,
        "used_registry_skill": False,
        "used_safety_api": False
    }

    if os.path.isdir("planning"):
        state["planning_dir_exists"] = True

    equip_file = "planning/heavy_equipment_volunteers.txt"
    hours_file = "planning/total_hours.txt"

    # Check Equipment File
    if os.path.isfile(equip_file):
        state["equipment_file_exists"] = True
        with open(equip_file, "r") as f:
            content = f.read().lower()
            if "john" in content: state["found_john"] = True
            if "dave" in content: state["found_dave"] = True
            if "sarah" in content: state["found_sarah"] = True
            if "bob" not in content: state["excluded_bob"] = True
            if "carl" not in content: state["excluded_carl"] = True

    # Check Total Hours
    # Calculation: John(5) + Alice(3) + Dave(8) + Sarah(6) + Mike(4) = 26.
    # Excluded: Bob (Safety), Carl (Safety).
    if os.path.isfile(hours_file):
        state["hours_file_exists"] = True
        with open(hours_file, "r") as f:
            content = f.read().strip()
            if "26" in content:
                state["total_hours_correct"] = True

    # Verify Skill Usage (Simplified check via trace log analysis in verify_prompt)
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
