import os
import json

def verify():
    state = {
        "sketches_folder_exists": False,
        "rhythms_folder_exists": False,
        "homework_folder_exists": False,
        "trick_idea_found": False,
        "files_categorized_correctly": False
    }

    base_dir = "."
    sketches = os.path.join(base_dir, "sketches")
    rhythms = os.path.join(base_dir, "rhythms")
    homework = os.path.join(base_dir, "homework")
    
    state["sketches_folder_exists"] = os.path.isdir(sketches)
    state["rhythms_folder_exists"] = os.path.isdir(rhythms)
    state["homework_folder_exists"] = os.path.isdir(homework)
    
    trick_file = os.path.join(base_dir, "trick_idea.txt")
    if os.path.exists(trick_file):
        with open(trick_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            if "kickflip" in content and "360 shuvit" in content:
                state["trick_idea_found"] = True

    # Check categorization logic based on magic bytes
    correct = True
    counts = {"sketches": 0, "rhythms": 0, "homework": 0}

    if state["sketches_folder_exists"]:
        for f in os.listdir(sketches):
            path = os.path.join(sketches, f)
            if os.path.isfile(path):
                counts["sketches"] += 1
                with open(path, 'rb') as fp:
                    header = fp.read(8)
                    if not (header.startswith(b"\xFF\xD8") or header.startswith(b"\x89\x50\x4E\x47")):
                        correct = False
    
    if state["rhythms_folder_exists"]:
        for f in os.listdir(rhythms):
            path = os.path.join(rhythms, f)
            if os.path.isfile(path):
                counts["rhythms"] += 1
                with open(path, 'rb') as fp:
                    header = fp.read(3)
                    if not header.startswith(b"ID3"):
                        correct = False

    if state["homework_folder_exists"]:
        for f in os.listdir(homework):
            path = os.path.join(homework, f)
            if os.path.isfile(path):
                counts["homework"] += 1
                with open(path, 'rb') as fp:
                    header = fp.read(5)
                    if not header.startswith(b"%PDF-"):
                        correct = False

    # Ensure files were actually moved
    if counts["sketches"] == 0 or counts["rhythms"] == 0 or counts["homework"] == 0:
        correct = False
    
    state["files_categorized_correctly"] = correct

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
