import os
import json
import sys

def verify():
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    briefing_dir = os.path.join(workdir, "briefing")
    
    state = {
        "briefing_file_exists": False,
        "has_fake_00": False,
        "has_bad_888": False,
        "no_false_positives": True
    }

    if os.path.exists(briefing_dir) and os.path.isdir(briefing_dir):
        files = os.listdir(briefing_dir)
        if len(files) > 0:
            state["briefing_file_exists"] = True
            
            content = ""
            for file_name in files:
                file_path = os.path.join(briefing_dir, file_name)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content += f.read()

            if "CA-9FAKE00" in content:
                state["has_fake_00"] = True
            if "CA-BAD888" in content:
                state["has_bad_888"] = True

            valid_plates = ["CA-5GTR222", "CA-1ABC123", "CA-8HJK999", "CA-2XYZ555", "CA-7TYU444"]
            for valid in valid_plates:
                if valid in content:
                    state["no_false_positives"] = False

    state_file_path = os.path.join(workdir, "state.json")
    with open(state_file_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
