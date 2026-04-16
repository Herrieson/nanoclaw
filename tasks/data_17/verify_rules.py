import os
import json

def verify():
    base_dir = "."
    state = {
        "clean_inventory_exists": False,
        "purchase_order_exists": False,
        "correct_cherry_deficit": False,
        "correct_maple_deficit": False
    }

    inv_path = os.path.join(base_dir, "clean_inventory.csv")
    po_path = os.path.join(base_dir, "purchase_order.txt")

    if os.path.exists(inv_path):
        state["clean_inventory_exists"] = True

    if os.path.exists(po_path):
        state["purchase_order_exists"] = True
        with open(po_path, 'r') as f:
            content = f.read()
            # Cherry needs 120 more inches
            if "Cherry 1x6: need 120 more linear inches" in content:
                state["correct_cherry_deficit"] = True
            # Maple needs 40 more inches
            if "Maple 1x4: need 40 more linear inches" in content:
                state["correct_maple_deficit"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
