import os
import json

def verify():
    base_dir = "."
    roster_path = os.path.join(base_dir, "final_roster.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_attendees": False,
        "no_canceled_attendees": False,
        "no_unoriented_attendees": False,
        "correct_role_updates": False,
        "exact_match": False
    }

    if not os.path.exists(roster_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(roster_path, 'r', encoding='utf-8') as f:
            roster = json.load(f)
        state["is_valid_json"] = True
    except Exception:
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    if not isinstance(roster, list):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    # Extract names and roles
    extracted_data = {item.get("name", "").lower(): item for item in roster}
    names = set(extracted_data.keys())

    # Expected valid attendees: Emily Clark, Michael Torres, David Kim, Jessica Alba
    expected_names = {"emily clark", "michael torres", "david kim", "jessica alba"}
    
    # Canceled: Sarah Jenkins
    # Missed orientation: Tom Hardy, Chloe Price
    invalid_names = {"sarah jenkins", "tom hardy", "chloe price"}

    if expected_names.issubset(names):
        state["correct_attendees"] = True

    if not any(invalid_name in names for invalid_name in {"sarah jenkins"}):
        state["no_canceled_attendees"] = True

    if not any(invalid_name in names for invalid_name in {"tom hardy", "chloe price"}):
        state["no_unoriented_attendees"] = True

    # Check Michael's role update
    michael_data = extracted_data.get("michael torres", {})
    if "wardrobe assistant" in michael_data.get("final_role", "").lower():
        state["correct_role_updates"] = True

    if state["correct_attendees"] and state["no_canceled_attendees"] and state["no_unoriented_attendees"] and len(names) == len(expected_names):
        state["exact_match"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
