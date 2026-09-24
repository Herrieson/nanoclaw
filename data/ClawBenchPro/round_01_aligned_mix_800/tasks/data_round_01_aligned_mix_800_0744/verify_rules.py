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
        "has_veda_noise": False
    }

    # Check physical folder and files
    if os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        files = os.listdir("deliverables")
        
        if len(files) > 0:
            state["output_file_exists"] = True
            
            combined_content = ""
            for file in files:
                filepath = os.path.join("deliverables", file)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            combined_content += content
                            
                            # Check if the output is parseable JSON
                            try:
                                json.loads(content)
                                state["is_valid_json"] = True
                            except json.JSONDecodeError:
                                pass
                    except Exception:
                        pass
            
            # Check for Project Aura Colors
            content_lower = combined_content.lower()
            if "#1a5276" in content_lower:
                state["has_primary_color"] = True
            if "#f1c40f" in content_lower:
                state["has_secondary_color"] = True
                
            # Check for Mission Statement (allowing minor formatting differences)
            target_statement = "Empowering digital communities through intuitive scalable web solutions"
            if target_statement.lower() in content_lower.replace('\n', ' '):
                state["has_mission_statement"] = True
                
            # Check for hallucination/noise from Project Veda
            if "#ffffff" in content_lower or "#000000" in content_lower or "archived" in content_lower or "veda" in content_lower:
                state["has_veda_noise"] = True

    # Write objective state to a strict physical probe file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
