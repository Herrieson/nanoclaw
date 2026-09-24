import os
import json
import re

def verify():
    state = {
        "expedite_folder_created": False,
        "summary_file_exists": False,
        "valid_json_format": False,
        "correct_shortages_calculated": False,
        "correct_carrier_selected": False
    }

    folder_path = "expedite_action"
    file_path = os.path.join(folder_path, "summary.json")

    if os.path.isdir(folder_path):
        state["expedite_folder_created"] = True

    if os.path.exists(file_path):
        state["summary_file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json_format"] = True
            
            dump_str = json.dumps(data).lower()
            
            # The exact deficits should be calculated via ERP tool:
            # EV-101: 5000 needed (2000+3000) - 4500 stock = 500
            # EV-102: 900 needed (400+500) - 800 stock = 100
            # EV-103: 150 needed (100+50) - 120 stock = 30
            # EV-104: 60 needed (20+40) - 50 stock = 10
            
            has_500 = bool(re.search(r'\b500\b', dump_str))
            has_100 = bool(re.search(r'\b100\b', dump_str))
            has_30 = bool(re.search(r'\b30\b', dump_str))
            has_10 = bool(re.search(r'\b10\b', dump_str))
            
            if has_500 and has_100 and has_30 and has_10:
                state["correct_shortages_calculated"] = True
                
            # The cheapest ACTIVE Same-Day carrier from the LLM-Mocked API is Carrier D ($3.90/lb)
            if "carrier d" in dump_str:
                state["correct_carrier_selected"] = True

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
