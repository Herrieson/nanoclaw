import os
import json

def verify():
    base_dir = "."
    truth_file = os.path.join(base_dir, ".truth.json")
    
    state = {
        "guitar_tabs_dir_exists": False,
        "lesson_plans_dir_exists": False,
        "total_expected_files": 0,
        "correctly_decoded_and_named": 0,
        "correctly_categorized": 0,
        "errors": []
    }
    
    if not os.path.exists(truth_file):
        state["errors"].append("Truth file missing. Environment was not built correctly.")
        return state
        
    with open(truth_file, "r", encoding="utf-8") as f:
        truth_data = json.load(f)
        
    state["total_expected_files"] = len(truth_data)
    
    tabs_dir = os.path.join(base_dir, "Guitar_Tabs")
    lessons_dir = os.path.join(base_dir, "Lesson_Plans")
    
    state["guitar_tabs_dir_exists"] = os.path.isdir(tabs_dir)
    state["lesson_plans_dir_exists"] = os.path.isdir(lessons_dir)
    
    found_titles = set()
    
    for target_dir, expected_type in [(tabs_dir, "tab"), (lessons_dir, "lesson")]:
        if not os.path.exists(target_dir):
            continue
            
        for filename in os.listdir(target_dir):
            if not filename.endswith(".txt"):
                continue
                
            title_guess = filename[:-4]
            file_path = os.path.join(target_dir, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if it was successfully decoded
            if "[PRANKED]" in content or not content.startswith("Title:"):
                state["errors"].append(f"File {filename} is not decoded properly or missing header.")
                continue
                
            # Verify against truth data
            if title_guess in truth_data:
                found_titles.add(title_guess)
                state["correctly_decoded_and_named"] += 1
                
                if truth_data[title_guess]["type"] == expected_type:
                    state["correctly_categorized"] += 1
                else:
                    state["errors"].append(f"File {filename} categorized incorrectly.")
            else:
                state["errors"].append(f"File {filename} has an incorrect or unexpected title.")

    # Output structured state
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
