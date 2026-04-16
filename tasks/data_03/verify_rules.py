import os
import json

def verify():
    target_file = "trip_prep/shopping_list.json"
    result = {
        "file_exists": False,
        "json_valid": False,
        "total_cost_correct": False,
        "items_correct": False,
        "found_cost": None,
        "found_items": None
    }

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        result["json_valid"] = True
    except:
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    # Logic:
    # Sausages: need 9, have 2 -> buy 7. Cost = 7 * 1.50 = 10.50
    # Buns: need 5, have 12 -> buy 0.
    # Mustard: need 1, have 1 -> buy 0.
    # Tortillas: need 10, have 0 -> buy 10. Cost = 10 * 0.20 = 2.00
    # Beef: need 2, have 0 -> buy 2. Cost = 2 * 5.00 = 10.00
    # Salsa: need 2, have 1 -> buy 1. Cost = 1 * 4.00 = 4.00
    # Total cost = 10.50 + 2.00 + 10.00 + 4.00 = 26.50

    expected_cost = 26.50
    expected_items = {
        "sausages": 7,
        "tortillas": 10,
        "beef": 2,
        "salsa": 1
    }

    found_cost = data.get("total_cost")
    found_items = data.get("items", {})

    result["found_cost"] = found_cost
    result["found_items"] = found_items

    if found_cost == expected_cost:
        result["total_cost_correct"] = True
    
    # Check if expected items are in found_items and quantities match
    # Ignore items with 0 quantity if they included them
    items_match = True
    for k, v in expected_items.items():
        if found_items.get(k) != v:
            items_match = False
            break
    
    # Ensure they didn't buy things they don't need
    for k, v in found_items.items():
        if v > 0 and k not in expected_items:
            items_match = False
            break

    result["items_correct"] = items_match

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
