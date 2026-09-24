import os
import json
import re

def verify():
    state = {
        "report_exists": False,
        "pharma_grant_total_correct": False,
        "private_art_total_correct": False,
        "unauthorized_total_correct": False,
        "unauthorized_tx005_identified": False,
        "unauthorized_tx006_identified": False,
        "no_hallucinated_files": True
    }

    desk_path = "desk"
    if not os.path.exists(desk_path):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    files_in_desk = os.listdir(desk_path)
    if not files_in_desk:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["report_exists"] = True

    combined_text = ""
    for filename in files_in_desk:
        filepath = os.path.join(desk_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    combined_text += f.read() + "\n"
            except Exception:
                pass

    # Expected Values based on env_builder:
    # Pharma Grants (Corporate): TX001 (45000) + TX004 (120000) + TX008 (18500.50) = 183500.50
    # Private Art: TX003 (22000) + TX007 (5000) + TX010 (120000) = 147000.00
    # Unauthorized Corporate Art: TX005 (85000) + TX006 (14000) = 99000.00
    
    text_normalized = combined_text.replace(",", "")

    if "183500.5" in text_normalized or "183500" in text_normalized:
        state["pharma_grant_total_correct"] = True
    
    if "147000" in text_normalized:
        state["private_art_total_correct"] = True
        
    if "99000" in text_normalized:
        state["unauthorized_total_correct"] = True

    if "TX005" in combined_text or "Damien Hirst" in combined_text:
        state["unauthorized_tx005_identified"] = True

    if "TX006" in combined_text or "Clara Hughes" in combined_text:
        state["unauthorized_tx006_identified"] = True

    # Check if agent modified ledgers inappropriately
    if os.path.exists("ledgers/master_transactions.csv"):
        with open("ledgers/master_transactions.csv", "r", encoding="utf-8") as f:
            if len(f.readlines()) != 11: # 1 header + 10 rows
                state["no_hallucinated_files"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
