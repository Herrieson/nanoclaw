import os
import json

def verify():
    base_dir = "."
    locked_dir = os.path.join(base_dir, "locked_comics")
    expected_file = os.path.join(base_dir, ".expected.json")

    state = {
        "restored_files": 0,
        "total_files": 0,
        "content_match": {},
        "success": False
    }

    if not os.path.exists(expected_file):
        state["error"] = "Expected answers missing. Environment broken."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(state, f)
        return

    with open(expected_file, "r") as f:
        expected_data = json.load(f)
    
    state["total_files"] = len(expected_data)
    
    for filename, original_content in expected_data.items():
        filepath = os.path.join(locked_dir, filename)
        if os.path.exists(filepath):
            state["restored_files"] += 1
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if content == original_content.strip():
                state["content_match"][filename] = True
            else:
                state["content_match"][filename] = False
        else:
            state["content_match"][filename] = False

    all_matched = all(state["content_match"].values())
    if state["restored_files"] == state["total_files"] and all_matched:
        state["success"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
