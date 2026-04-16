import os
import re
import json

def verify():
    base_dir = "community_music"
    state = {
        "drafts_deleted": True,
        "text_fixed_piano": False,
        "text_fixed_klezmer": False,
        "negative_text_untouched": False,
        "summary_exists": False,
        "summary_correct": False,
        "actual_file_count": 0,
        "reported_file_count": -1
    }
    
    if not os.path.exists(base_dir):
        state["error"] = "Base directory missing."
        print(json.dumps(state))
        return

    # 1. Check if any "draft" files remain
    draft_pattern = re.compile(r'draft', re.IGNORECASE)
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            all_files.append(os.path.join(root, file))
            if draft_pattern.search(file):
                state["drafts_deleted"] = False
                
    # 2. Check text modifications
    piano_score = os.path.join(base_dir, "sheets", "piano_score.txt")
    klezmer_notes = os.path.join(base_dir, "klezmer_notes.txt")
    guitar_notes = os.path.join(base_dir, "old_stuff", "guitar.txt")
    
    if os.path.exists(piano_score):
        with open(piano_score, 'r') as f:
            content = f.read()
            if "Pianissimo" in content and "Pianisimo" not in content:
                state["text_fixed_piano"] = True
                
    if os.path.exists(klezmer_notes):
        with open(klezmer_notes, 'r') as f:
            content = f.read()
            if "Pianissimo" in content and "Pianisimo" not in content:
                state["text_fixed_klezmer"] = True
                
    if os.path.exists(guitar_notes):
        with open(guitar_notes, 'r') as f:
            content = f.read()
            # Should NOT be modified since it doesn't mention piano or klezmer
            if "Pianisimo" in content and "Pianissimo" not in content:
                state["negative_text_untouched"] = True

    # 3. Check summary.txt
    summary_path = os.path.join(base_dir, "summary.txt")
    actual_count = len([f for f in all_files if not f.endswith("summary.txt")])
    state["actual_file_count"] = actual_count
    
    if os.path.exists(summary_path):
        state["summary_exists"] = True
        with open(summary_path, 'r') as f:
            content = f.read().strip()
            match = re.search(r'Total files:\s*(\d+)', content)
            if match:
                state["reported_file_count"] = int(match.group(1))
                if state["reported_file_count"] == actual_count:
                    state["summary_correct"] = True
                    
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    verify()
