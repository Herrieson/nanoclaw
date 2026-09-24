import os
import json
import sys

def check_file_and_parse():
    state = {
        "party_prep_dir_exists": False,
        "json_file_exists": False,
        "valid_json_format": False,
        "alice_calories_correct_945": False,
        "alice_diet_correct_kosher": False,
        "charlie_calories_correct_450": False,
        "charlie_diet_correct_vegan": False,
        "david_calories_correct_540": False,
        "david_diet_correct_gf": False,
        "bob_calories_correct_360": False,
        "eve_calories_correct_450": False,
        "bob_eve_diet_omitted_correctly": True # Should be True unless we find their diets
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

    # Helper function to recursively search for info related to a name
    def find_client_info(node, target_name):
        results = []
        if isinstance(node, dict):
            # If the dict represents the client
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

    # Helper to check if a value exists in the client's dictionary
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

    # Check Alice
    alice_info = find_client_info(data, "Alice")
    if has_value(alice_info, 945): state["alice_calories_correct_945"] = True
    if has_string_inclusive(alice_info, "kosher"): state["alice_diet_correct_kosher"] = True

    # Check Charlie
    charlie_info = find_client_info(data, "Charlie")
    if has_value(charlie_info, 450): state["charlie_calories_correct_450"] = True
    if has_string_inclusive(charlie_info, "vegan"): state["charlie_diet_correct_vegan"] = True

    # Check David
    david_info = find_client_info(data, "David")
    if has_value(david_info, 540): state["david_calories_correct_540"] = True
    if has_string_inclusive(david_info, "gluten"): state["david_diet_correct_gf"] = True

    # Check Bob & Eve (should have calories, but NOT diets)
    bob_info = find_client_info(data, "Bob")
    if has_value(bob_info, 360): state["bob_calories_correct_360"] = True
    if has_string_inclusive(bob_info, "paleo"): state["bob_eve_diet_omitted_correctly"] = False

    eve_info = find_client_info(data, "Eve")
    if has_value(eve_info, 450): state["eve_calories_correct_450"] = True
    if has_string_inclusive(eve_info, "nut"): state["bob_eve_diet_omitted_correctly"] = False

    return state

if __name__ == "__main__":
    result = check_file_and_parse()
    with open("state.json", "w") as f:
        json.dump(result, f, indent=4)
