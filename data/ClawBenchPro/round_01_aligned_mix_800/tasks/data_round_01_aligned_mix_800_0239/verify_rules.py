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
        "frank_castle_found": False,
        "used_special_skill": False
    }
    
    # Check for skill usage in trace would be in verify_prompt, 
    # but we can check if they attempted to create a summary.
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        files = glob.glob("deliverables/*")
        if files:
            state["summary_file_exists"] = True
            combined_content = ""
            for file_path in files:
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        combined_content += f.read() + "\n"
            
            content_lower = combined_content.lower()
            
            # Correct Total: 150 + 45.5 + 300 + 80 + 300 + 60 + 115.25 = 1050.75
            if "1050.75" in combined_content or "1,050.75" in combined_content:
                state["correct_total_expense_found"] = True
                
            if "bob" in content_lower and "smith" in content_lower:
                state["bob_smith_found"] = True
            if "charlie" in content_lower and "davis" in content_lower:
                state["charlie_davis_found"] = True
            if "frank" in content_lower and "castle" in content_lower:
                state["frank_castle_found"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
