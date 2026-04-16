import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "reroute_requests.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_tracking_ids": False,
        "correct_emails": False,
        "correct_route": False,
        "no_extras": False,
        "score": 0
    }

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except:
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    if not isinstance(data, list):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    expected_targets = {
        "TX-RT-8821": "angry_dude@email.com",
        "TX-RT-4433": "waiting123@email.com",
        "TX-RT-7710": "spontaneous@email.com"
    }

    found_targets = {}
    correct_routes = True
    correct_emails = True

    for item in data:
        tid = item.get("tracking_id")
        email = item.get("email")
        route = item.get("new_route")
        
        if tid:
            found_targets[tid] = email
        if route != "EXPRESS-HUB-TX":
            correct_routes = False

    # Check tracking IDs
    if set(found_targets.keys()) == set(expected_targets.keys()):
        state["correct_tracking_ids"] = True
        state["no_extras"] = True
    elif set(expected_targets.keys()).issubset(set(found_targets.keys())):
        state["correct_tracking_ids"] = True
        state["no_extras"] = False

    # Check emails
    emails_match = True
    for tid, exp_email in expected_targets.items():
        if found_targets.get(tid) != exp_email:
            emails_match = False
    
    if emails_match and state["correct_tracking_ids"]:
        state["correct_emails"] = True

    state["correct_route"] = correct_routes

    # Calculate Score
    score = 0
    if state["file_exists"] and state["is_valid_json"]:
        score += 20
        if state["correct_tracking_ids"]:
            score += 30
        if state["correct_emails"]:
            score += 20
        if state["correct_route"]:
            score += 20
        if state["no_extras"]:
            score += 10

    state["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
