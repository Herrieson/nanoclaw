import os
import json

def verify():
    state = {
        "prep_dir_exists": False,
        "has_report_file": False,
        "identified_missouri_mule": False,
        "excluded_irish_sunrise": True,
        "excluded_midwest_fidget": True,
        "calculated_correct_tips": False
    }

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
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            combined_text += f.read().lower()
                    except Exception:
                        pass
            
            # Check for cocktail identification
            if "missouri mule" in combined_text:
                state["identified_missouri_mule"] = True
            if "irish sunrise" in combined_text:
                state["excluded_irish_sunrise"] = False
            if "midwest fidget" in combined_text:
                state["excluded_midwest_fidget"] = False
                
            # Check for the correct math sum (350)
            # Variations like $350, 350.00, 350
            if "350" in combined_text:
                state["calculated_correct_tips"] = True

    # Output pure objective state
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
