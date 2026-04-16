import os
import json

def verify():
    base_dir = "."
    flagged_path = os.path.join(base_dir, "flagged.json")
    clean_path = os.path.join(base_dir, "clean_log.json")
    
    state = {
        "flagged_exists": False,
        "clean_exists": False,
        "flagged_valid_json": False,
        "clean_valid_json": False,
        "flagged_count": 0,
        "clean_count": 0,
        "flagged_patients": [],
        "clean_patients": [],
        "errors": []
    }

    if os.path.exists(flagged_path):
        state["flagged_exists"] = True
        try:
            with open(flagged_path, "r") as f:
                data = json.load(f)
                state["flagged_valid_json"] = True
                state["flagged_count"] = len(data)
                state["flagged_patients"] = sorted([str(item.get("patient_id", "")) for item in data])
                # Check typing
                if len(data) > 0 and not isinstance(data[0].get("quantity"), int):
                    state["errors"].append("Quantity in flagged.json is not an integer.")
        except Exception as e:
            state["errors"].append(f"Error parsing flagged.json: {e}")

    if os.path.exists(clean_path):
        state["clean_exists"] = True
        try:
            with open(clean_path, "r") as f:
                data = json.load(f)
                state["clean_valid_json"] = True
                state["clean_count"] = len(data)
                state["clean_patients"] = sorted([str(item.get("patient_id", "")) for item in data])
                if len(data) > 0 and not isinstance(data[0].get("quantity"), int):
                    state["errors"].append("Quantity in clean_log.json is not an integer.")
        except Exception as e:
            state["errors"].append(f"Error parsing clean_log.json: {e}")

    # Expected logic:
    # PT-1029: Clean
    # PT-9912: Flagged (Adderall, Qty 60 > 30, Prescriber missing)
    # PT-5511: Clean (Oxycodone, Qty 15 <= 30, Dr present)
    # PT-3321: Clean
    # PT-4444: Flagged (Oxycodone, Qty 45 > 30, Dr MISSING)
    # PT-0001: Clean
    # PT-7777: Clean (Adderall, Qty 30 <= 30, Dr present)
    # PT-8888: Flagged (Oxycodone, Qty 20 <= 30, but Dr is missing)
    # PT-1234: Clean (Metformin, Dr missing but not Schedule II)
    
    state["expected_flagged"] = ["PT-4444", "PT-8888", "PT-9912"]
    state["expected_clean"] = ["PT-0001", "PT-1029", "PT-1234", "PT-3321", "PT-5511", "PT-7777"]

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
