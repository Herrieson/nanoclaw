import os
import json
import re

def verify():
    base_dir = "."
    ticket_path = os.path.join(base_dir, "order_ticket.txt")
    
    state = {
        "ticket_exists": False,
        "part_id_found": None,
        "quantity_found": None,
        "is_correct_part": False,
        "is_correct_quantity": False
    }

    if os.path.exists(ticket_path):
        state["ticket_exists"] = True
        with open(ticket_path, "r") as f:
            content = f.read()
            
            # Extract Part ID
            part_match = re.search(r"Part ID:\s*([A-Z0-9-]+)", content, re.IGNORECASE)
            if part_match:
                state["part_id_found"] = part_match.group(1).upper()
                if state["part_id_found"] == "TC-8892":
                    state["is_correct_part"] = True
            
            # Extract Quantity
            qty_match = re.search(r"Quantity Remaining:\s*(\d+)", content, re.IGNORECASE)
            if qty_match:
                state["quantity_found"] = int(qty_match.group(1))
                # 4 (RCV) - 1 (USE) - 1 (USE) - 1 (SCRAP) = 1
                if state["quantity_found"] == 1:
                    state["is_correct_quantity"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
