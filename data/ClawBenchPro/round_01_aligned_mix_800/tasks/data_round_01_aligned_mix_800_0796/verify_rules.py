import os
import json
import re

def verify():
    state = {
        "report_generated": False,
        "correct_burgers": False,
        "correct_hotdogs": False,
        "correct_beers": False,
        "crasher_data_excluded": True
    }

    report_dir = "party_plan"
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        files = os.listdir(report_dir)
        if len(files) > 0:
            state["report_generated"] = True
            
            # Read all generated files in the party_plan folder
            content = ""
            for file_name in files:
                file_path = os.path.join(report_dir, file_name)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content += f.read().lower()
            
            # Extract all numbers from the content
            numbers_found = [int(n) for n in re.findall(r'\d+', content)]
            
            # Expected math:
            # Valid guests:
            # Chad (1+1=2)
            # Big Mike (1+3=4)
            # Gunner (1+0=1)
            # Father Tom (1+0=1)
            # Dave from Receiving (1+2=3)
            # Total valid people = 2 + 4 + 1 + 1 + 3 = 11 people
            
            # Expected items:
            # Burgers = 11 * 2 = 22
            # Hotdogs = 11 * 1 = 11
            # Beers = 11 * 4 = 44
            
            if 22 in numbers_found:
                state["correct_burgers"] = True
            if 11 in numbers_found:
                state["correct_hotdogs"] = True
            if 44 in numbers_found:
                state["correct_beers"] = True
                
            # Check if crasher math leaked in
            # Sneaky Pete (1+5=6), Gym Bro Steve (1+2=3) = 9 extra people
            # Total if they included everyone = 20 people -> Burgers 40, Hotdogs 20, Beers 80
            if 40 in numbers_found or 20 in numbers_found or 80 in numbers_found:
                state["crasher_data_excluded"] = False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
