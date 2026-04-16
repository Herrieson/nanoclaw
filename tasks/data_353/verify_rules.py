import os
import json
import re

def verify():
    state = {
        "script_exists": False,
        "shortage_file_exists": False,
        "correct_shortage_calculated": False,
        "extracted_value": None
    }

    # Check if script is created
    if os.path.exists("calculate_shortage.py"):
        state["script_exists"] = True

    # Check if output file exists
    if os.path.exists("shortage.txt"):
        state["shortage_file_exists"] = True
        try:
            with open("shortage.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                state["extracted_value"] = content
                
                # Check for the correct answer '850'
                if re.search(r'\b850\b', content):
                    state["correct_shortage_calculated"] = True
        except Exception:
            pass

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
