import os
import json
import re

def verify():
    base_dir = "."
    result = {
        "reorder_list_exists": False,
        "reorder_list_correct": False,
        "workshop_time_exists": False,
        "workshop_time_correct": False
    }

    reorder_path = os.path.join(base_dir, "reorder_list.json")
    if os.path.exists(reorder_path):
        result["reorder_list_exists"] = True
        try:
            with open(reorder_path, "r") as f:
                data = json.load(f)
            # The correct IDs are 101, 104, 105, 108. 
            # 107 has stock 12, reorder 12 (not strictly lower)
            expected = {101, 104, 105, 108}
            # Handle both string and int parsed lists
            actual = set([int(x) for x in data])
            if actual == expected:
                result["reorder_list_correct"] = True
        except Exception:
            pass

    workshop_path = os.path.join(base_dir, "workshop_time.txt")
    if os.path.exists(workshop_path):
        result["workshop_time_exists"] = True
        try:
            with open(workshop_path, "r") as f:
                content = f.read().strip()
            # Most people are available Tuesday 14:00-15:00
            if "Tuesday 14:00" in content:
                result["workshop_time_correct"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
