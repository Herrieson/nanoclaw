import os
import json
import re

def verify():
    state = {
        "deliverables_folder_exists": False,
        "report_file_exists": False,
        "correct_guest_count_found": False,
        "correct_tortillas_to_buy": False,
        "correct_chicken_to_buy": False,
        "correct_cheese_to_buy": False,
        "correct_sauce_to_buy": False
    }

    deliverables_path = "deliverables"
    
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True
        
        files = os.listdir(deliverables_path)
        if len(files) > 0:
            state["report_file_exists"] = True
            
            full_content = ""
            for file in files:
                file_path = os.path.join(deliverables_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        full_content += f.read() + "\n"
            
            # The agent should have calculated 19 regular guests
            if "19" in full_content:
                state["correct_guest_count_found"] = True
                
            # Tortillas to buy: 37 (12 * 4.75 = 57. 57 - 20 = 37)
            if "37" in full_content:
                state["correct_tortillas_to_buy"] = True
                
            # Chicken to buy: 8 (2 * 4.75 = 9.5. 9.5 - 1.5 = 8.0)
            if re.search(r'\b8\.?0?\b', full_content):
                state["correct_chicken_to_buy"] = True
                
            # Cheese to buy: 66 (16 * 4.75 = 76. 76 - 10 = 66)
            if re.search(r'\b66\.?0?\b', full_content):
                state["correct_cheese_to_buy"] = True
                
            # Sauce to buy: 2.75 (1 * 4.75 = 4.75. 4.75 - 2 = 2.75)
            if "2.75" in full_content:
                state["correct_sauce_to_buy"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
