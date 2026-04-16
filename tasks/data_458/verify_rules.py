import os
import json

def verify():
    base_dir = "."
    payload_path = os.path.join(base_dir, "upload_payload.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "is_list": False,
        "correct_keys": False,
        "dates_normalized": False,
        "species_title_cased": False,
        "verified_logic_correct": False,
        "total_records_processed": 0
    }

    if not os.path.exists(payload_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(payload_path, 'r', encoding='utf-8') as f:
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
    
    state["is_list"] = True
    state["total_records_processed"] = len(data)

    required_keys = {"observation_date", "species", "count", "is_verified"}
    
    dates_ok = True
    species_ok = True
    keys_ok = True
    logic_ok = True

    # Expected verification logic based on notes:
    # 04/15 -> Robin -> true
    # 04/16 -> Blue Jay -> false
    # 04/18 -> Cardinal -> true
    # 04/20 -> Warbler -> true
    # 04/22 -> Charity bird -> false
    # 04/25 -> Mourning Dove -> true
    
    expected_logic = {
        "American Robin": True,
        "Blue Jay": False,
        "Northern Cardinal": True,
        "Cerulean Warbler": True,
        "Mourning Dove": True
    }

    for item in data:
        if not required_keys.issubset(set(item.keys())):
            keys_ok = False
        
        date = item.get("observation_date", "")
        if len(date) != 10 or date[4] != '-' or date[7] != '-':
            dates_ok = False
            
        species = item.get("species", "")
        if species != species.title() or species.startswith(" ") or species.endswith(" "):
            species_ok = False
            
        # Check logic
        if species in expected_logic:
            if item.get("is_verified") != expected_logic[species]:
                logic_ok = False

    state["correct_keys"] = keys_ok
    state["dates_normalized"] = dates_ok
    state["species_title_cased"] = species_ok
    state["verified_logic_correct"] = logic_ok

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
