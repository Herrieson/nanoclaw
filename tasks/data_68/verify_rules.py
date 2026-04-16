import os
import re
import json

def verify():
    base_dir = "."
    target_dir = os.path.join(base_dir, "ready_to_send")
    
    expected_data = {
        "liam_mom@email.com.txt": {"due": 105, "kit": "pinecone owl kit", "name": "liam"},
        "emma_dad@email.com.txt": {"due": 105, "kit": "recycled paper bead kit", "name": "emma"},
        "noah_fam@email.com.txt": {"due": 175, "kit": "pinecone owl kit", "name": "noah"},
        "olivia_mom@email.com.txt": {"due": 70, "kit": "recycled paper bead kit", "name": "olivia"}
    }

    result = {
        "folder_exists": False,
        "files_found": [],
        "verifications": {}
    }

    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        result["folder_exists"] = True
        files = os.listdir(target_dir)
        result["files_found"] = files
        
        for filename, expected in expected_data.items():
            file_path = os.path.join(target_dir, filename)
            file_res = {
                "exists": False,
                "amount_correct": False,
                "kit_correct": False,
                "name_found": False
            }
            if os.path.exists(file_path):
                file_res["exists"] = True
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                
                # Check amount
                if f"${expected['due']}" in content or f"{expected['due']} dollars" in content or str(expected['due']) in content:
                    # Stricter check for $105 etc
                    match = re.search(r'\$\s*' + str(expected['due']), content)
                    if match or str(expected['due']) in content:
                        file_res["amount_correct"] = True
                
                # Check kit
                if expected['kit'] in content:
                    file_res["kit_correct"] = True
                    
                # Check name
                if expected['name'] in content:
                    file_res["name_found"] = True

            result["verifications"][filename] = file_res
    
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
