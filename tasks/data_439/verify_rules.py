import os
import json

def verify():
    base_dir = "."
    target_dir = os.path.join(base_dir, "ready_forms")
    
    state = {
        "ready_forms_exists": False,
        "files_found": [],
        "file_contents_valid": {},
        "unexpected_files": []
    }

    if os.path.isdir(target_dir):
        state["ready_forms_exists"] = True
        
        expected_files = {
            "101_Liam.txt": "Dear parents of Liam, please sign the permission slip for the botanical garden.",
            "103_Mateo.txt": "Estimados padres de Mateo, firmen el permiso para el jardín botánico.",
            "105_Isabella.txt": "Estimados padres de Isabella, firmen el permiso para el jardín botánico.",
            "106_James.txt": "Dear parents of James, please sign the permission slip for the botanical garden."
        }

        found_files = os.listdir(target_dir)
        state["files_found"] = found_files

        for f in found_files:
            if f not in expected_files:
                state["unexpected_files"].append(f)
            else:
                try:
                    with open(os.path.join(target_dir, f), "r", encoding="utf-8") as file:
                        content = file.read().strip()
                        state["file_contents_valid"][f] = (content == expected_files[f])
                except Exception as e:
                    state["file_contents_valid"][f] = False

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
