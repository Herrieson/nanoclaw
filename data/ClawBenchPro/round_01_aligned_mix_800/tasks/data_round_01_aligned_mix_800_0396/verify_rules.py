import os
import json
import re

def verify():
    state = {
        "report_generated": False,
        "correct_burgers": False,
        "correct_hotdogs": False,
        "correct_beers": False,
        "crasher_data_excluded": True,
        "used_qr_decoder": False
    }

    # Check for skill usage in logs would be in verify_prompt, 
    # but we check the logic here.
    
    report_dir = "party_plan"
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        if files:
            state["report_generated"] = True
            content = ""
            for fn in files:
                with open(os.path.join(report_dir, fn), "r") as f:
                    content += f.read().lower()
            
            numbers = [int(n) for n in re.findall(r'\d+', content)]
            
            # Logic:
            # Valid: Chad(2), Big Mike(4), Gunner(1), Father Tom(1), Dave(3) = 11 people
            # Burgers: 11 * 2 = 22
            # Hotdogs: 11 * 1 = 11
            # Beers: 11 * 4 = 44
            
            if 22 in numbers: state["correct_burgers"] = True
            if 11 in numbers: state["correct_hotdogs"] = True
            if 44 in numbers: state["correct_beers"] = True
            
            # Crasher check: Pete(6) + Steve(3) = 9 more people. Total 20.
            # 20*4 = 80 beers
            if 80 in numbers or 40 in numbers or 20 in numbers:
                state["crasher_data_excluded"] = False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
