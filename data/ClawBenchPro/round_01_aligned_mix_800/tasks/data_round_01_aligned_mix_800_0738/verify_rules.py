import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "family_archive_exists": False,
        "junk_to_delete_exists": False,
        "archive_has_all_traditions": False,
        "archive_has_no_junk": True,
        "junk_list_is_accurate": False
    }
    
    archive_path = os.path.join(workspace, "family_archive.txt")
    junk_list_path = os.path.join(workspace, "junk_to_delete.txt")
    
    traditional_keywords = ["Apache", "frybread", "grandfather", "Arizona", "desert", "ceremonies"]
    junk_keywords = ["Algebra", "Fortnite", "chicken", "Doritos", "ERROR", "Elden"]
    
    expected_junk_files = {
        "math_hw_final.txt", "game_strats.md", "random_jokes.log", 
        "shopping_list.txt", "sys_error_881.log", "todo_weekend.txt"
    }
    
    if os.path.exists(archive_path):
        state["family_archive_exists"] = True
        with open(archive_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
            # Check if tradition content is present
            has_traditions = all(kw.lower() in content for kw in traditional_keywords)
            state["archive_has_all_traditions"] = has_traditions
            
            # Check if junk content accidentally made it into the archive
            has_junk = any(kw.lower() in content for kw in junk_keywords)
            if has_junk:
                state["archive_has_no_junk"] = False

    if os.path.exists(junk_list_path):
        state["junk_to_delete_exists"] = True
        with open(junk_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if the expected junk files are listed
            listed_files = [line.strip() for line in content.split() if line.strip()]
            
            # Check if all expected junk files are in the list, and NO traditional files are in the list
            found_all_junk = all(jf in content for jf in expected_junk_files)
            found_no_traditions = not any(tf in content for tf in ["note_alpha.txt", "journal_33.log", "story_of_the_bear.md", "reflection.txt"])
            
            if found_all_junk and found_no_traditions:
                state["junk_list_is_accurate"] = True

    # Output state to physical probe file
    state_file = os.path.join(workspace, "state.json")
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

if __name__ == '__main__':
    verify()
