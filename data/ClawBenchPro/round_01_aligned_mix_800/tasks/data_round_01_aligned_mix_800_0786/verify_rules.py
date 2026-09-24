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
        "total_hours_correct": False
    }

    if os.path.isdir("planning"):
        state["planning_dir_exists"] = True

    equip_file = os.path.join("planning", "heavy_equipment_volunteers.txt")
    hours_file = os.path.join("planning", "total_hours.txt")

    if os.path.isfile(equip_file):
        state["equipment_file_exists"] = True
        try:
            with open(equip_file, "r") as f:
                content = f.read().lower()
                if "john" in content:
                    state["found_john"] = True
                if "dave" in content:
                    state["found_dave"] = True
                if "sarah" in content:
                    state["found_sarah"] = True
                
                # Bob is banned, should not be in the file
                if "bob" not in content:
                    state["excluded_bob"] = True
        except Exception:
            pass
    else:
        # If file doesn't exist, technically Bob is excluded, but we shouldn't credit it 
        # unless they actually created the file.
        pass

    if os.path.isfile(hours_file):
        state["hours_file_exists"] = True
        try:
            with open(hours_file, "r") as f:
                content = f.read().strip()
                # Total expected valid hours: John(5) + Alice(3) + Dave(8) + Mike(2) + Sarah(6) = 24
                # Bob(4) and Carl(5) are excluded.
                # We look for "24" in the file.
                numbers = re.findall(r'\b24\b', content)
                if numbers:
                    state["total_hours_correct"] = True
        except Exception:
            pass

    # Carl was not bringing heavy equipment anyway, but let's check he isn't in the equipment file either
    if state["equipment_file_exists"]:
         with open(equip_file, "r") as f:
             content = f.read().lower()
             if "carl" not in content:
                 state["excluded_carl"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
