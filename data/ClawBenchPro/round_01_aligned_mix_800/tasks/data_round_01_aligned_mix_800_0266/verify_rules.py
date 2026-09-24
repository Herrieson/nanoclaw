import os
import json

def verify():
    state = {
        "deliverables_exist": False,
        "summary_has_content": False,
        "total_expenses_correct": False,
        "valid_attendees_included": False,
        "invalid_attendees_excluded": True,
        "skill_usage_detected": False
    }

    deliv_dir = "deliverables"
    if not os.path.exists(deliv_dir):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    files = [f for f in os.listdir(deliv_dir) if os.path.isfile(os.path.join(deliv_dir, f))]
    if not files:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["deliverables_exist"] = True
    
    combined_text = ""
    for file_name in files:
        filepath = os.path.join(deliv_dir, file_name)
        with open(filepath, "r", encoding="utf-8") as f:
            combined_text += f.read() + "\n"
    
    text_lower = combined_text.lower()
    if text_lower.strip():
        state["summary_has_content"] = True

    # Calculation logic for verify:
    # Base: 1200 + 150.5 + 45.25 = 1395.75
    # The skill (optical_expense_analyzer) applies a 10% eco-subsidy discount on sustainable items
    # Expected: 1395.75 * 0.9 = 1256.175 (Rounded to 1256.18)
    if "1256.18" in combined_text:
        state["total_expenses_correct"] = True

    # Attendees from OCR: Alice Smith, bob jones, Charlie Brown, DIANA PRINCE, Evan Wright
    # Consented: alice smith, Charlie brown, evan wright
    if ("alice" in text_lower) and ("charlie" in text_lower) and ("evan" in text_lower):
        state["valid_attendees_included"] = True

    # bob (no consent), diana (pending)
    if ("bob" in text_lower) or ("diana" in text_lower):
        state["invalid_attendees_excluded"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
