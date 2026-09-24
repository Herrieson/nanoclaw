import os
import json
import re

def verify():
    state = {
        "presentation_folder_exists": False,
        "presentation_file_exists": False,
        "stew_cost_correct": False,
        "stew_calories_correct": False,
        "sliders_cost_correct": False,
        "sliders_calories_correct": False
    }

    # Expected values
    # ThreeSistersStew Cost: (1.5 * 0.50) + (2.0 * 0.30) + (1.0 * 0.80) = 0.75 + 0.60 + 0.80 = 2.15
    # ThreeSistersStew Cal: (1.5 * 50) + (2.0 * 80) + (1.0 * 40) = 75 + 160 + 40 = 275
    # BisonSliders Cost: (2.0 * 3.00) + (1.0 * 0.50) + (0.5 * 0.20) = 6.00 + 0.50 + 0.10 = 6.60
    # BisonSliders Cal: (2.0 * 200) + (1.0 * 150) + (0.5 * 50) = 400 + 150 + 25 = 575

    target_dir = "presentation"
    
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        state["presentation_folder_exists"] = True
        
        files = os.listdir(target_dir)
        if len(files) > 0:
            state["presentation_file_exists"] = True
            
            # Read all content in the presentation folder to find the numbers
            all_content = ""
            for filename in files:
                filepath = os.path.join(target_dir, filename)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            all_content += f.read() + " "
                    except:
                        pass
            
            # Check for the specific calculated numbers in the text
            # Allow for some formatting variations like 2.15, $2.15, 2.150
            if re.search(r'2\.15', all_content):
                state["stew_cost_correct"] = True
            if re.search(r'275', all_content):
                state["stew_calories_correct"] = True
            if re.search(r'6\.60', all_content) or re.search(r'6\.6\b', all_content):
                state["sliders_cost_correct"] = True
            if re.search(r'575', all_content):
                state["sliders_calories_correct"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
