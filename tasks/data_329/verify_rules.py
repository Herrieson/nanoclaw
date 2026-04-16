import os
import json

def verify():
    file_path = "final_money.txt"
    result = {
        "file_exists": False,
        "has_juana": False,
        "has_lucia": False,
        "correct_amount": False
    }
    
    if os.path.exists(file_path):
        result["file_exists"] = True
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "juana" in content:
                result["has_juana"] = True
            if "lucia" in content:
                result["has_lucia"] = True
            if "224.50" in content or "224.5" in content:
                result["correct_amount"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
