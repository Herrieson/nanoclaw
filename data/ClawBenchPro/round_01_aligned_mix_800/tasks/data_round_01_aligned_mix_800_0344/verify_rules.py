import os
import json

def verify():
    state = {
        "deliverables_folder_exists": False,
        "output_file_exists": False,
        "is_valid_json": False,
        "has_primary_color": False,
        "has_secondary_color": False,
        "has_mission_statement": False,
        "used_correct_skills": False,
        "has_veda_noise": False
    }

    # Check physical folder and files
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        files = [f for f in os.listdir("deliverables") if os.path.isfile(os.path.join("deliverables", f))]
        
        if len(files) > 0:
            state["output_file_exists"] = True
            
            combined_content = ""
            for file in files:
                filepath = os.path.join("deliverables", file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        combined_content += content
                        try:
                            json.loads(content)
                            state["is_valid_json"] = True
                        except: pass
                except: pass
            
            content_lower = combined_content.lower()
            if "#1a5276" in content_lower:
                state["has_primary_color"] = True
            if "#f1c40f" in content_lower:
                state["has_secondary_color"] = True
                
            target_statement = "Empowering digital communities through intuitive scalable web solutions"
            if target_statement.lower() in content_lower.replace('\n', ' '):
                state["has_mission_statement"] = True
                
            if "#ffffff" in content_lower or "veda" in content_lower:
                state["has_veda_noise"] = True

    # Check trace for skill usage (this will be further checked by verify_prompt.md)
    # We write a placeholder here; the actual check is in the LLM judge.
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
