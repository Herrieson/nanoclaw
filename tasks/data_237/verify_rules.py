import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "top_candidates.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "is_list": False,
        "length_is_3": False,
        "correct_order_and_data": False,
        "extracted_data": None,
        "errors": []
    }

    if not os.path.exists(target_file):
        state["errors"].append("top_candidates.json not found.")
        return json.dumps(state)

    state["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
            state["extracted_data"] = data
            state["is_valid_json"] = True
    except Exception as e:
        state["errors"].append(f"JSON parsing error: {str(e)}")
        return json.dumps(state)

    if not isinstance(data, list):
        state["errors"].append("Root JSON element is not a list.")
        return json.dumps(state)
    
    state["is_list"] = True

    if len(data) == 3:
        state["length_is_3"] = True
    else:
        state["errors"].append(f"List contains {len(data)} items instead of 3.")

    expected_ids = ["CID-1042", "CID-8831", "CID-9910"]
    try:
        actual_ids = [item.get("id") for item in data]
        if actual_ids == expected_ids:
            # Check fields
            valid_fields = True
            for item in data:
                if not all(k in item for k in ["id", "smiles", "affinity", "toxicity"]):
                    valid_fields = False
                    state["errors"].append(f"Missing keys in object: {item}")
                    break
            if valid_fields:
                state["correct_order_and_data"] = True
        else:
            state["errors"].append(f"Expected IDs in order {expected_ids}, got {actual_ids}")
    except Exception as e:
        state["errors"].append(f"Data validation error: {str(e)}")

    print(json.dumps(state, indent=2))
    
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

    return json.dumps(state)

if __name__ == "__main__":
    verify()
