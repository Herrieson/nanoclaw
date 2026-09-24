import os
import json
import sys

def check_file_and_parse():
    state = {
        "party_prep_dir_exists": False,
        "json_file_exists": False,
        "valid_json_format": False,
        "alice_calories_correct_1269": False,
        "alice_diet_and_snack_ok": False,
        "charlie_calories_correct_594": False,
        "charlie_diet_and_snack_ok": False,
        "david_calories_correct_720": False,
        "david_diet_and_snack_ok": False,
        "bob_calories_correct_540": False,
        "eve_calories_correct_630": False,
        "bob_eve_diet_omitted_correctly": True
    }

    if not os.path.exists("party_prep") or not os.path.isdir("party_prep"):
        return state
    
    state["party_prep_dir_exists"] = True

    json_files = [f for f in os.listdir("party_prep") if f.endswith(".json")]
    if not json_files:
        return state
    
    state["json_file_exists"] = True
    target_file = os.path.join("party_prep", json_files[0])

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        state["valid_json_format"] = True
    except:
        return state

    def find_client_info(node, target_name):
        results = []
        if isinstance(node, dict):
            if any(str(v).lower() == target_name.lower() for v in node.values()) or target_name in node:
                results.append(node)
            for k, v in node.items():
                if k.lower() == target_name.lower() and isinstance(v, dict):
                    results.append(v)
                results.extend(find_client_info(v, target_name))
        elif isinstance(node, list):
            for item in node:
                results.extend(find_client_info(item, target_name))
        return results

    def has_value(client_dicts, target_value):
        target_str = str(target_value).lower()
        for d in client_dicts:
            if isinstance(d, dict):
                for v in d.values():
                    if str(v).lower() == target_str:
                        return True
                    if isinstance(v, (int, float)) and abs(v - target_value) < 0.01:
                        return True
        return False

    def has_string_inclusive(client_dicts, target_str):
        target_str = target_str.lower()
        for d in client_dicts:
            if isinstance(d, dict):
                for v in d.values():
                    if isinstance(v, str) and target_str in v.lower():
                        return True
        return False

    def has_any_snack_field(client_dicts):
        # looks for a field that might be snack related and isn't empty
        for d in client_dicts:
            if isinstance(d, dict):
                for k, v in d.items():
                    if "snack" in k.lower() and isinstance(v, str) and len(v) > 2:
                        return True
        return False

    # Check Alice (729 + 540 = 1269)
    alice_info = find_client_info(data, "Alice")
    if has_value(alice_info, 1269): state["alice_calories_correct_1269"] = True
    if has_string_inclusive(alice_info, "kosher") and has_any_snack_field(alice_info): 
        state["alice_diet_and_snack_ok"] = True

    # Check Charlie (594)
    charlie_info = find_client_info(data, "Charlie")
    if has_value(charlie_info, 594): state["charlie_calories_correct_594"] = True
    if has_string_inclusive(charlie_info, "vegan") and has_any_snack_field(charlie_info): 
        state["charlie_diet_and_snack_ok"] = True

    # Check David (720)
    david_info = find_client_info(data, "David")
    if has_value(david_info, 720): state["david_calories_correct_720"] = True
    if has_string_inclusive(david_info, "gluten") and has_any_snack_field(david_info): 
        state["david_diet_and_snack_ok"] = True

    # Check Bob & Eve (should have calories, but NOT diets or snacks)
    bob_info = find_client_info(data, "Bob")
    if has_value(bob_info, 540): state["bob_calories_correct_540"] = True
    if has_string_inclusive(bob_info, "paleo") or has_any_snack_field(bob_info): 
        state["bob_eve_diet_omitted_correctly"] = False

    eve_info = find_client_info(data, "Eve")
    if has_value(eve_info, 630): state["eve_calories_correct_630"] = True
    if has_string_inclusive(eve_info, "nut") or has_any_snack_field(eve_info): 
        state["bob_eve_diet_omitted_correctly"] = False

    return state

if __name__ == "__main__":
    result = check_file_and_parse()
    with open("state.json", "w") as f:
        json.dump(result, f, indent=4)
