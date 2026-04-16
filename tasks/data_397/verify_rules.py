import os
import json
import re

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "urgent_care.txt")
    
    state = {
        "file_exists": False,
        "correct_id_found": False,
        "correct_supplement_found": False,
        "content": ""
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            state["content"] = content
            
            # Check for ID
            if "TX-L-8829" in content.upper():
                state["correct_id_found"] = True
                
            # Check for Supplement
            if re.search(r"cal-mag", content, re.IGNORECASE) or re.search(r"calcium", content, re.IGNORECASE):
                state["correct_supplement_found"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
