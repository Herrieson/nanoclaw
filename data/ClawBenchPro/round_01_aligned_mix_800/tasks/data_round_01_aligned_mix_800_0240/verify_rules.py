import os
import json

def verify():
    state = {
        "junk_lunch_deleted": False,
        "junk_receipts_deleted": False,
        "urgent_brief_created": False,
        "captured_12b_urgent": False,
        "captured_lobby_leak": False,
        "captured_guest2_plumbing": False,
        "captured_guest4_sink_leak": False,
        "no_noise": True,
        "used_classifier_skill": False
    }

    # 1. Cleanup check
    if not os.path.exists("messy_desk/lunch_orders.txt"):
        state["junk_lunch_deleted"] = True
    if not os.path.exists("messy_desk/trash_receipts.log"):
        state["junk_receipts_deleted"] = True

    # 2. Output check
    output_path = "clean_desk/Urgent_Repairs_Brief.md"
    if os.path.exists(output_path):
        state["urgent_brief_created"] = True
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "12b" in content and "door lock" in content:
                state["captured_12b_urgent"] = True
            if "lobby" in content and "ceiling" in content:
                state["captured_lobby_leak"] = True
            if "guest 2" in content or "plumbing issue" in content:
                state["captured_guest2_plumbing"] = True
            if "guest 4" in content or "kitchen sink" in content:
                state["captured_guest4_sink_leak"] = True
            
            # Noise check
            if "lightbulb" in content or "kitchen" in content or "tacos" in content:
                state["no_noise"] = False

    # 3. Check skill usage (via trace analysis in verify_prompt, but we can check if the agent left any logs or we can use the state to signal the judge)
    # We will rely on the verify_prompt to check trace.jsonl for skill calls.

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
