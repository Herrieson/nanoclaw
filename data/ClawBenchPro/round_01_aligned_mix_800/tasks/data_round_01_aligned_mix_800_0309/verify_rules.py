import os
import json

def verify():
    state = {
        "prep_dir_exists": False,
        "has_report_file": False,
        "identified_missouri_mule_only": False,
        "calculated_correct_net_tips": False,
        "used_audio_skill": False
    }

    # Check for skill usage via trace (this is a placeholder for logic handled in verify_prompt)
    
    prep_path = "prep_work"
    if os.path.exists(prep_path) and os.path.isdir(prep_path):
        state["prep_dir_exists"] = True
        files = os.listdir(prep_path)
        if files:
            state["has_report_file"] = True
            combined_text = ""
            for filename in files:
                filepath = os.path.join(prep_path, filename)
                if os.path.isfile(filepath):
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        combined_text += f.read().lower()
            
            # The only viable drink is Missouri Mule.
            # Irish Sunrise needs Grenadine (smashed).
            # Midwest Fidget needs Bourbon (out) and Simple Syrup (mold).
            if "missouri mule" in combined_text and "irish sunrise" not in combined_text and "midwest fidget" not in combined_text:
                state["identified_missouri_mule_only"] = True
            
            # Net tips should be 308
            if "308" in combined_text:
                state["calculated_correct_net_tips"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
