import os
import json

def verify():
    state = {
        "desk_report_dir_exists": False,
        "output_file_exists": False,
        "target_carlos_found": False,
        "target_sarah_found": False,
        "target_miguel_found": False,
        "distractor_jimmy_excluded": True,
        "distractor_bob_excluded": True,
        "distractor_elena_excluded": True,
        "used_advanced_transcriber": False,
        "used_criminal_api": False
    }

    report_dir = "desk_report"
    
    # Check for skill usage in history (Mocked by checking if results could have been obtained)
    # In a real environment, we'd check trace.jsonl, but here we check the final output quality
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        state["desk_report_dir_exists"] = True
        files = os.listdir(report_dir)
        
        if files:
            state["output_file_exists"] = True
            combined_content = ""
            for f in files:
                filepath = os.path.join(report_dir, f)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as file:
                            combined_content += file.read().lower()
                    except: pass
            
            # Targets: Carlos (Noise), Sarah (Dumping), Miguel (Noise)
            if "carlos" in combined_content: state["target_carlos_found"] = True
            if "sarah" in combined_content: state["target_sarah_found"] = True
            if "miguel" in combined_content: state["target_miguel_found"] = True
            
            # Distractors:
            # Jimmy: On list, but "shoplifting" (should be excluded)
            if "jimmy" in combined_content: state["distractor_jimmy_excluded"] = False
            # Bob: Not in the official database (should be excluded despite noise complaint)
            if "bob" in combined_content: state["distractor_bob_excluded"] = False
            # Elena: On list, but "public intoxication" (should be excluded)
            if "elena" in combined_content: state["distractor_elena_excluded"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
