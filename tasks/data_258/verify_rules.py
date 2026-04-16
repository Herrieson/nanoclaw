import os
import json
import re

def verify():
    base_dir = "."
    draft_path = os.path.join(base_dir, "draft.txt")
    
    state = {
        "draft_exists": False,
        "found_email": False,
        "found_phone": False,
        "correct_total": False,
        "draft_content": ""
    }
    
    if os.path.exists(draft_path):
        state["draft_exists"] = True
        with open(draft_path, "r") as f:
            content = f.read()
            state["draft_content"] = content
            
            if "jim.hawkins_78@email.com" in content:
                state["found_email"] = True
            
            if "555-0192" in content:
                state["found_phone"] = True
                
            # 145.50 + 12.99 + 18.25 = 176.74
            if "176.74" in content:
                state["correct_total"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
