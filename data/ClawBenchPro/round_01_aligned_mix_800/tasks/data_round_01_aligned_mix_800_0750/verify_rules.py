import os
import json
import re

def verify():
    state = {
        "desk_drawer_created": False,
        "summary_file_exists": False,
        "identified_E1": False,
        "identified_E2": False,
        "identified_E3": False,
        "correct_healthy_yield_calculated": False
    }

    if os.path.exists("desk_drawer") and os.path.isdir("desk_drawer"):
        state["desk_drawer_created"] = True
        
        files = [f for f in os.listdir("desk_drawer") if os.path.isfile(os.path.join("desk_drawer", f))]
        if len(files) > 0:
            state["summary_file_exists"] = True
            
            combined_text = ""
            for filename in files:
                filepath = os.path.join("desk_drawer", filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        combined_text += f.read().upper()
                except Exception:
                    pass

            # Check for identification of compromised plots
            if "E1" in combined_text:
                state["identified_E1"] = True
            if "E2" in combined_text:
                state["identified_E2"] = True
            if "E3" in combined_text:
                state["identified_E3"] = True

            # The healthy yield sum should be:
            # W1 (5000) + W2 (4800) + W3 (4200) + N1 (5500) + S1 (6000) = 25500
            # We remove commas to make text searching robust.
            text_no_punctuation = combined_text.replace(",", "").replace(".", "")
            if "25500" in text_no_punctuation:
                state["correct_healthy_yield_calculated"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
