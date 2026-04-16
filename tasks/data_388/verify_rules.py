import os
import json

def verify():
    target_file = "mysterious_drive/vip_pass.txt"
    result = {
        "pass_file_exists": False,
        "correct_content": False,
        "score": 0
    }

    if os.path.exists(target_file):
        result["pass_file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read()
            # Check if the bug was fixed and the correct name was used
            if "ULTIMATE VIP ARCADE PASS FOR: Marcus" in content:
                result["correct_content"] = True
                result["score"] = 100
            elif "Marcus" in content:
                # Partial credit if they made a pass but maybe formatted it wrong
                result["score"] = 50

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
