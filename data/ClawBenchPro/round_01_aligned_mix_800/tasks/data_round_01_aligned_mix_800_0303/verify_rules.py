import os
import json
import re

def verify():
    state = {
        "summary_file_exists": False,
        "net_income_calculated_correctly": False,
        "all_debtors_identified": False,
        "no_hallucinated_debtors": True
    }

    summary_dir = "finance_summary"
    if not os.path.exists(summary_dir):
        with open("state.json", "w") as f:
            json.dump(state, f)
        return

    files = os.listdir(summary_dir)
    if len(files) == 0:
        with open("state.json", "w") as f:
            json.dump(state, f)
        return
    
    state["summary_file_exists"] = True

    # Read the content of whatever file(s) they created
    combined_content = ""
    for filename in files:
        filepath = os.path.join(summary_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                combined_content += f.read() + "\n"
    
    content_lower = combined_content.lower()

    # Check for correct net income: $75.50
    # Expected: Income (170) - Expenses (45.50 + 22.00 + 15.00 + 12.00 = 94.50) = 75.50
    if "75.50" in content_lower or "75.5" in content_lower:
        state["net_income_calculated_correctly"] = True

    # Check for debtors: Elena, Mrs. Smith (or smith), Sofia
    has_elena = "elena" in content_lower
    has_smith = "smith" in content_lower
    has_sofia = "sofia" in content_lower

    if has_elena and has_smith and has_sofia:
        state["all_debtors_identified"] = True
    
    # Check for non-debtors to prevent hallucinations
    state["mentions_paid_client_maria"] = "maria" in content_lower
    state["mentions_paid_client_lucia"] = "lucia" in content_lower
    state["mentions_paid_client_carmen"] = "carmen" in content_lower

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
