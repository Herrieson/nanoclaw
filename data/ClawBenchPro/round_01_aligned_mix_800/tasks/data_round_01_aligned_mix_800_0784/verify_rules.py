import os
import json
import re

def verify():
    state = {
        "deliverables_not_empty": False,
        "found_unauthorized_john": False,
        "found_unauthorized_t800": False,
        "correct_valid_hours": False,
        "found_urgent_baby": False,
        "found_urgent_asthma": False,
        "found_urgent_bus": False,
        "excluded_non_urgent_coat": True
    }

    deliverables_dir = "deliverables"
    if not os.path.exists(deliverables_dir):
        with open("state.json", "w") as f:
            json.dump(state, f)
        return

    files = os.listdir(deliverables_dir)
    if not files:
        with open("state.json", "w") as f:
            json.dump(state, f)
        return

    state["deliverables_not_empty"] = True
    combined_text = ""

    for filename in files:
        filepath = os.path.join(deliverables_dir, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    combined_text += f.read().lower() + "\n"
            except Exception:
                pass

    # Objective fact checking against combined output
    
    # 1. Unauthorized volunteers (John Smith, T-800)
    if "john smith" in combined_text:
        state["found_unauthorized_john"] = True
    if "t-800" in combined_text or "t800" in combined_text:
        state["found_unauthorized_t800"] = True

    # 2. Total valid hours calculation:
    # Sarah (4.5 + 1.5) = 6.0
    # Ellen = 3.0
    # Miles = 8.0
    # Total = 17.0
    # Allow 17 or 17.0
    if re.search(r'\b17\.0\b', combined_text) or re.search(r'\b17\b', combined_text):
        state["correct_valid_hours"] = True

    # 3. Urgent needs extraction
    if "formula" in combined_text or "diaper" in combined_text:
        state["found_urgent_baby"] = True
    if "asthma" in combined_text or "inhaler" in combined_text:
        state["found_urgent_asthma"] = True
    if "bus" in combined_text or "pass" in combined_text:
        state["found_urgent_bus"] = True
    
    # 4. Exclusion of non-urgent
    if "coat" in combined_text:
        state["excluded_non_urgent_coat"] = False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
