import os
import json

def verify():
    state = {
        "junk_lunch_deleted": False,
        "junk_receipts_deleted": False,
        "urgent_file_exists": False,
        "captured_12b_urgent": False,
        "captured_lobby_leak": False,
        "captured_guest2_urgent": False,
        "captured_guest4_leak": False,
        "no_non_urgent_noise": True
    }

    # 1. Check if trash is deleted
    if not os.path.exists("messy_desk/lunch_orders.txt"):
        state["junk_lunch_deleted"] = True
    if not os.path.exists("messy_desk/trash_receipts.log"):
        state["junk_receipts_deleted"] = True

    # 2. Find the output file
    clean_desk_files = []
    if os.path.exists("clean_desk"):
        clean_desk_files = os.listdir("clean_desk")
    
    output_file = None
    for f in clean_desk_files:
        if f.endswith(".md") or "urgent" in f.lower() or "repair" in f.lower():
            output_file = os.path.join("clean_desk", f)
            break
            
    if output_file and os.path.isfile(output_file):
        state["urgent_file_exists"] = True
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            if "door lock is completely broken" in content or "unit 12b" in content:
                state["captured_12b_urgent"] = True
            if "coming from the ceiling" in content or "lobby" in content:
                state["captured_lobby_leak"] = True
            if "plumbing issue" in content or "guest 2" in content:
                state["captured_guest2_urgent"] = True
            if "under the kitchen sink" in content or "guest 4" in content:
                state["captured_guest4_leak"] = True
                
            # Check for noise (non-urgent lines)
            if "lightbulb" in content or "paint is chipping" in content or "loved the kitchen" in content or "asking price" in content:
                state["no_non_urgent_noise"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
