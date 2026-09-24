import os
import json

def verify():
    state = {
        "deliverables_exist": False,
        "summary_has_content": False,
        "total_expenses_correct": False,
        "valid_attendees_included": False,
        "invalid_attendees_excluded": True
    }

    deliv_dir = "deliverables"
    if not os.path.exists(deliv_dir):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    files = os.listdir(deliv_dir)
    if not files:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["deliverables_exist"] = True
    
    combined_text = ""
    for file_name in files:
        filepath = os.path.join(deliv_dir, file_name)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    combined_text += f.read() + "\n"
            except Exception:
                pass
    
    text_lower = combined_text.lower()
    if text_lower.strip():
        state["summary_has_content"] = True

    # 1200.00 + 150.50 + 45.25 = 1395.75
    if "1395.75" in combined_text or "1,395.75" in combined_text:
        state["total_expenses_correct"] = True

    # Valid attendees based on cross-referencing attendees_notes.txt & signed consent in consent_logs.json
    if ("alice" in text_lower) and ("charlie" in text_lower) and ("evan" in text_lower):
        state["valid_attendees_included"] = True

    # Invalid attendees:
    # bob jones (no consent record)
    # diana prince (consent is 'pending', not signed)
    # frank ocean (not in attendees list) -> Not strictly checking frank, just making sure the core invalids from the event are removed
    if ("bob" in text_lower) or ("diana" in text_lower):
        state["invalid_attendees_excluded"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
