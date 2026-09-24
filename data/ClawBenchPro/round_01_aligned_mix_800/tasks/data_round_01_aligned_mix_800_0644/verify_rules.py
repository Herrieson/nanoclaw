import os
import json
import glob

def verify():
    state = {
        "deliverables_folder_exists": os.path.isdir("deliverables"),
        "json_files_found": [],
        "file_contents": {}
    }
    
    if state["deliverables_folder_exists"]:
        for f in glob.glob("deliverables/*.json"):
            filename = os.path.basename(f)
            state["json_files_found"].append(filename)
            try:
                with open(f, "r") as fh:
                    state["file_contents"][filename] = json.load(fh)
            except Exception as e:
                state["file_contents"][filename] = f"Invalid JSON or read error: {str(e)}"
                
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
