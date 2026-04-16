import os
import json

def verify():
    base_dir = "."
    result_file = os.path.join(base_dir, "failed_devices.json")
    
    state = {
        "json_exists": False,
        "valid_json": False,
        "found_devices": [],
        "expected_devices": ["PO-103", "IP-202", "PO-104", "IP-205"],
        "correct_ids": False,
        "has_reasons": False
    }

    if os.path.exists(result_file):
        state["json_exists"] = True
        try:
            with open(result_file, "r") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            if isinstance(data, list):
                found_ids = []
                all_have_reasons = True
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        found_ids.append(item["id"])
                    if "reason" not in item or not item["reason"]:
                        all_have_reasons = False
                
                state["found_devices"] = found_ids
                state["has_reasons"] = all_have_reasons
                
                if sorted(found_ids) == sorted(state["expected_devices"]):
                    state["correct_ids"] = True

        except Exception as e:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
