import os
import json
import sys

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "final_invites.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_count": False,
        "correct_entries": False,
        "details": []
    }

    if not os.path.exists(target_file):
        state["details"].append(f"File {target_file} not found.")
        print(json.dumps(state))
        return

    state["file_exists"] = True

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except json.JSONDecodeError:
        state["details"].append("File is not valid JSON.")
        print(json.dumps(state))
        return

    if not isinstance(data, list):
        state["details"].append("JSON root is not a list.")
        print(json.dumps(state))
        return

    # Expected valid students after filtering:
    # Alice Smith (Valid, not opted out)
    # Bobby Jones (Valid, OPTED OUT) -> Exclude
    # Charlie Brown (Corrupted: no grade) -> Exclude
    # David Miller (Corrupted: ERROR) -> Exclude
    # Eve Davis (Valid, not opted out)
    # Frank White (Corrupted: CORRUPTED) -> Exclude
    # Grace Lee (Valid, OPTED OUT) -> Exclude
    
    # Expected final list: Alice Smith, Eve Davis
    expected_students = ["Alice Smith", "Eve Davis"]
    
    if len(data) == 2:
        state["correct_count"] = True
    else:
        state["details"].append(f"Expected 2 entries, got {len(data)}.")

    found_alice = False
    found_eve = False
    format_correct = True

    for entry in data:
        if not all(k in entry for k in ("student_name", "email", "art_title")):
            format_correct = False
            state["details"].append("Missing required keys in an entry.")
            break
        
        if entry.get("student_name") == "Alice Smith":
            if entry.get("email") == "asm_parent@example.com" and entry.get("art_title") == "My Little Garden":
                found_alice = True
        elif entry.get("student_name") == "Eve Davis":
            if entry.get("email") == "eve_parents@example.com" and entry.get("art_title") == "Sunset Over Hudson":
                found_eve = True

    if format_correct and found_alice and found_eve and state["correct_count"]:
        state["correct_entries"] = True
    else:
        state["details"].append("Entries do not exactly match the expected filtered data.")

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

    print(json.dumps(state))

if __name__ == "__main__":
    verify()
