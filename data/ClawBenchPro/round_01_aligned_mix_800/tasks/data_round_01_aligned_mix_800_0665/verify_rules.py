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
        "distractor_elena_excluded": True
    }

    report_dir = "desk_report"
    
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
                    except Exception:
                        pass
            
            # Check targets (Must be included)
            if "carlos mendez" in combined_content or "carlos" in combined_content:
                state["target_carlos_found"] = True
            if "sarah smith" in combined_content or "sarah" in combined_content:
                state["target_sarah_found"] = True
            if "miguel santos" in combined_content or "miguel" in combined_content:
                state["target_miguel_found"] = True
                
            # Check distractors (Must be excluded)
            # Jimmy (On watchlist, but crime is shoplifting)
            if "jimmy" in combined_content or "o'connor" in combined_content:
                state["distractor_jimmy_excluded"] = False
            # Bob (Crime is noise complaint, but NOT on watchlist)
            if "bob" in combined_content or "builder" in combined_content:
                state["distractor_bob_excluded"] = False
            # Elena (On watchlist, but crime is public intoxication)
            if "elena" in combined_content or "rostova" in combined_content:
                state["distractor_elena_excluded"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
