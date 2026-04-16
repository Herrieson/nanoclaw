import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "ohio_shipment_summary.json")
    
    state = {
        "file_exists": False,
        "is_valid_json": False,
        "total_correct": False,
        "batches_correct": False,
        "reported_total": None,
        "extracted_batches": {}
    }

    if not os.path.exists(target_file):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except json.JSONDecodeError:
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    reported_total = data.get("total_ohio_wearables", -1)
    state["reported_total"] = reported_total

    # Expected logic:
    # B001: WearableTech, 100 - 12 = 88, Ohio -> Included (88)
    # B002: BasicApparel -> WearableTech, 50, Ohio -> Included (50)
    # B003: WearableTech, 200, NewYork -> Ohio -> Included (200)
    # B004: WearableTech, 80 -> 0, Ohio -> Included (0) or excluded
    # Expected total: 88 + 50 + 200 = 338
    
    if reported_total == 338:
        state["total_correct"] = True

    batches = {}
    for key, val in data.items():
        if isinstance(val, dict):
            batches = val
            break
        elif isinstance(val, int) and key != "total_ohio_wearables":
            batches[key] = val
    
    state["extracted_batches"] = batches

    # Check if correct batches are identified with correct quantities
    correct_b001 = batches.get("B001") == 88
    correct_b002 = batches.get("B002") == 50
    correct_b003 = batches.get("B003") == 200
    b004_qty = batches.get("B004", 0)
    correct_b004 = (b004_qty == 0) # Can be absent or 0

    if correct_b001 and correct_b002 and correct_b003 and correct_b004:
        state["batches_correct"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
