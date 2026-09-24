import os
import json
import glob
import sys

def verify():
    # Set workspace
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "planning_docs_exists": False,
        "has_summary_file": False,
        "contains_correct_total_hours": False,
        "contains_certified_names": False,
        "excludes_uncertified_names": False
    }

    docs_dir = os.path.join(work_dir, "planning_docs")
    if os.path.exists(docs_dir) and os.path.isdir(docs_dir):
        state["planning_docs_exists"] = True
        files = glob.glob(os.path.join(docs_dir, "*"))
        if files:
            state["has_summary_file"] = True
            content = ""
            for file in files:
                if os.path.isfile(file):
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        content += f.read()
            
            # Correct hours calculation:
            # Valid certified: John Doe (5), Maria Garcia (8), Tom Smith (4), David Kim (6)
            # Sarah Lee is certified, but has -2 hours (invalid). 
            # Total = 5 + 8 + 4 + 6 = 23
            if "23" in content:
                state["contains_correct_total_hours"] = True
                
            certified_names = ["John Doe", "Maria Garcia", "David Kim", "Tom Smith"]
            uncertified_names = ["Alex P", "Zack W", "Linda B"]
            
            if all(name in content for name in certified_names):
                state["contains_certified_names"] = True
                
            if all(name not in content for name in uncertified_names):
                state["excludes_uncertified_names"] = True

    with open(os.path.join(work_dir, "state.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
