import os
import json
import re
import sys

def verify():
    # The agent's working directory is passed or assumed to be current
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    manifest_path = os.path.join(work_dir, "manifest.json")
    catering_path = os.path.join(work_dir, "catering_summary.txt")
    
    state = {
        "manifest_exists": False,
        "manifest_valid_json": False,
        "manifest_correct_students": False,
        "manifest_correct_data": False,
        "catering_exists": False,
        "catering_correct_counts": False
    }
    
    # Expected valid students (waiver_signed == 1): 101, 103, 104, 105, 107, 108
    expected_students = {
        101: {"name": "Alice Smith", "emergency_contact": "555-0101", "diet": "Vegan"},
        103: {"name": "Charlie Davis", "emergency_contact": "555-0103", "diet": "Gluten-Free"},
        104: {"name": "Diana Prince", "emergency_contact": "555-0104", "diet": "None"},
        105: {"name": "Evan Wright", "emergency_contact": "555-0105", "diet": "Vegetarian"},
        107: {"name": "George Miller", "emergency_contact": "555-0107", "diet": "None"},
        108: {"name": "Hannah Abbott", "emergency_contact": "555-0108", "diet": "Vegan"}
    }
    
    expected_counts = {
        "Vegan": 2,
        "Gluten-Free": 1,
        "None": 2,
        "Vegetarian": 1
    }
    
    if os.path.exists(manifest_path):
        state["manifest_exists"] = True
        try:
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)
            state["manifest_valid_json"] = True
            
            if isinstance(manifest_data, list):
                actual_ids = [s.get("id") for s in manifest_data]
                if sorted(actual_ids) == sorted(expected_students.keys()):
                    state["manifest_correct_students"] = True
                    
                    data_correct = True
                    for student in manifest_data:
                        sid = student.get("id")
                        if student.get("diet", "").lower() != expected_students[sid]["diet"].lower():
                            data_correct = False
                        if student.get("name") != expected_students[sid]["name"]:
                            data_correct = False
                    state["manifest_correct_data"] = data_correct
        except Exception:
            pass

    if os.path.exists(catering_path):
        state["catering_exists"] = True
        try:
            with open(catering_path, "r") as f:
                content = f.read().lower()
            
            # Use regex to find counts in the text
            counts_correct = True
            for diet, count in expected_counts.items():
                # Look for something like "vegan: 2" or "vegan - 2"
                pattern = rf"{diet.lower()}[\s:-]+{count}"
                if not re.search(pattern, content):
                    counts_correct = False
            state["catering_correct_counts"] = counts_correct
        except Exception:
            pass

    # Save verification state
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
