import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "video_link.txt")
    expected_content = "https://underground-skate.net/vid/1999_secret_footage.mp4"
    
    result = {
        "target_file_exists": False,
        "content_correct": False,
        "extracted_content": None
    }

    if os.path.exists(target_file):
        result["target_file_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                result["extracted_content"] = content
                if content == expected_content:
                    result["content_correct"] = True
        except Exception:
            pass

    # Save verification state
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

    print(json.dumps(result))

if __name__ == "__main__":
    verify()
