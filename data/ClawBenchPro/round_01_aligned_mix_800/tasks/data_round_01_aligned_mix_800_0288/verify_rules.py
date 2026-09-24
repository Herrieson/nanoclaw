import os
import json

def verify():
    state = {
        "report_directory_created": False,
        "report_file_exists": False,
        "defective_hubs_identified": False,
        "average_comfort_correct": False
    }

    if os.path.isdir("reports"):
        state["report_directory_created"] = True
        
        report_files = os.listdir("reports")
        if len(report_files) > 0:
            state["report_file_exists"] = True
            
            # Read all text from report files
            full_text = ""
            for file in report_files:
                file_path = os.path.join("reports", file)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        full_text += f.read().lower()
            
            # Check for specific defective hubs (Chicago and Atlanta)
            if "chicago" in full_text and "atlanta" in full_text:
                if "seattle" not in full_text and "dallas" not in full_text:
                    state["defective_hubs_identified"] = True
                    
            # Check for correct average comfort rating (3.5)
            # The ratings were 4, 3, 5, 2. Average is 14/4 = 3.5
            if "3.5" in full_text:
                state["average_comfort_correct"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
