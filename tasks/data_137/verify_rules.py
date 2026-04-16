import os
import json

def verify():
    base_dir = "."
    order_file = os.path.join(base_dir, "transfer_order.json")
    
    result = {
        "file_exists": False,
        "valid_json": False,
        "correct_order_id": False,
        "correct_destination": False,
        "correct_material": False,
        "exact_quantity_met": False,
        "no_overdraw": False,
        "errors": []
    }

    if not os.path.exists(order_file):
        result["errors"].append("transfer_order.json not found.")
        print(json.dumps(result))
        return

    result["file_exists"] = True

    try:
        with open(order_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["valid_json"] = True
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {str(e)}")
        print(json.dumps(result))
        return

    # Check basic fields
    if str(data.get("order_id")) == "992":
        result["correct_order_id"] = True
    else:
        result["errors"].append("Incorrect or missing order_id.")

    if data.get("destination") == "Assembly":
        result["correct_destination"] = True
    else:
        result["errors"].append("Incorrect or missing destination.")

    if data.get("material") == "Bamboo Fiber":
        result["correct_material"] = True
    else:
        result["errors"].append("Incorrect or missing material.")

    # Calculate expected state from notes
    # 11/01: R=500
    # 11/02 & 11/03 (correction): R=300, SA=200
    # 11/04: R=250, SA=200, P=50
    # 11/05: P loses 20 -> P=30
    # 11/06: SA to P (150) -> SA=50, P=180
    # 11/07: R to SB (30) -> R=220, SB=30
    # Final state: Receiving: 220, Storage_A: 50, Storage_B: 30, Prep: 180
    actual_stock = {
        "Receiving": 220,
        "Storage_A": 50,
        "Storage_B": 30,
        "Prep": 180
    }
    
    transfers = data.get("transfers", [])
    total_transferred = 0
    overdraw = False

    for t in transfers:
        src = t.get("source")
        qty = t.get("quantity", 0)
        
        # normalize source names slightly just in case
        src_clean = str(src).strip("[]")
        
        if src_clean not in actual_stock:
            result["errors"].append(f"Unknown source location: {src}")
            overdraw = True
            continue
            
        total_transferred += qty
        actual_stock[src_clean] -= qty
        
        if actual_stock[src_clean] < 0:
            result["errors"].append(f"Overdrew from {src_clean}. Had {actual_stock[src_clean] + qty}, tried to take {qty}.")
            overdraw = True

    if not overdraw:
        result["no_overdraw"] = True

    if total_transferred == 240:
        result["exact_quantity_met"] = True
    else:
        result["errors"].append(f"Expected to transfer exactly 240 units, but transferred {total_transferred}.")

    # Output the state
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    verify()
