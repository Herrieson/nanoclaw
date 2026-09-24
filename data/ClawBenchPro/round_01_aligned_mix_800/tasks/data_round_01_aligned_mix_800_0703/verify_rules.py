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
    # Allow 75.5, 75.50
    if "75.50" in content_lower or "75.5" in content_lower:
        state["net_income_calculated_correctly"] = True

    # Check for debtors: Elena, Mrs. Smith (or smith), Sofia
    has_elena = "elena" in content_lower
    has_smith = "smith" in content_lower
    has_sofia = "sofia" in content_lower

    if has_elena and has_smith and has_sofia:
        state["all_debtors_identified"] = True
    
    # Check for non-debtors (Maria, Lucia, Carmen) - if they are listed as owing, that's a hallucination
    # A simple proxy: if the file says "Maria owes" or something. Since we just want objective probes,
    # we'll check if the names "maria", "lucia", "carmen" appear in the output. If they do, they MIGHT
    # be hallucinated as debtors, OR just listed in a total ledger. We will just check if "maria" is 
    # anywhere near "owe" but a safer probe is seeing if they correctly extracted ONLY debtors.
    # Let's just pass this probe data to the LLM judge to decide. We will record if paid clients are mentioned.
    state["mentions_paid_client_maria"] = "maria" in content_lower
    state["mentions_paid_client_lucia"] = "lucia" in content_lower
    state["mentions_paid_client_carmen"] = "carmen" in content_lower

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
