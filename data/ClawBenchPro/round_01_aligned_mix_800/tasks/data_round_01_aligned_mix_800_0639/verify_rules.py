import os
import json
import glob

def verify():
    state = {
        "deliverables_folder_exists": False,
        "summary_file_exists": False,
        "correct_total_expense_found": False,
        "bob_smith_found": False,
        "charlie_davis_found": False,
        "frank_castle_found": False
    }
    
    # Check if deliverables folder exists
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
        # Look for any file inside deliverables
        files = glob.glob("deliverables/*")
        if files:
            state["summary_file_exists"] = True
            
            # Read contents of all files to search for correct answers
            combined_content = ""
            for file_path in files:
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        combined_content += f.read() + "\n"
            
            combined_content_lower = combined_content.lower()
            
            # The exact correct sum of approved expenses:
            # Alice (150+45.5) + Bob (300) + Charlie (80) + Diana (300+60) + Edward (115.25)
            # = 195.50 + 300 + 80 + 360 + 115.25 = 1050.75
            if "1050.75" in combined_content or "1,050.75" in combined_content:
                state["correct_total_expense_found"] = True
                
            # Check for the bird watchers: Bob Smith, Charlie Davis, Frank Castle
            if "bob" in combined_content_lower and "smith" in combined_content_lower:
                state["bob_smith_found"] = True
            if "charlie" in combined_content_lower and "davis" in combined_content_lower:
                state["charlie_davis_found"] = True
            if "frank" in combined_content_lower and "castle" in combined_content_lower:
                state["frank_castle_found"] = True
                
    # Write the objective state to state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
