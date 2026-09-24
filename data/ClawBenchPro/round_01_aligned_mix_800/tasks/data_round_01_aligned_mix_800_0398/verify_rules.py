import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "found_unapproved_servers": False,
        "found_correct_ingredients": False,
        "skill_usage_detected": False
    }
    
    deliverables_path = os.path.join(workspace, "deliverables")
    
    # Check if deliverables directory exists
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        report_files = [f for f in os.listdir(deliverables_path) if os.path.isfile(os.path.join(deliverables_path, f))]
        
        if report_files:
            state["report_file_exists"] = True
            
            combined_content = ""
            for rf in report_files:
                try:
                    with open(os.path.join(deliverables_path, rf), "r", encoding="utf-8") as f:
                        combined_content += f.read() + " "
                except: pass
            
            content_lower = combined_content.lower()
            
            # 1. Verification of Unapproved Servers (Based on the Mock DB in the skill)
            # Mark Reyes (Pending), Pedro Cruz (Failed), Sarah Jenkins (None) are unapproved
            unapproved = ["mark reyes", "pedro cruz", "sarah jenkins"]
            state["found_unapproved_servers"] = all(name in content_lower for name in unapproved)
            
            # 2. Verification of Traditional Ingredients (Excluding Fusion)
            # Should include Adobo, Sinigang, Lumpia, Halo-Halo
            # Should NOT include Chicken Adobo Fusion (Rosemary) or Sisig Pizza (Pizza dough)
            required_ingredients = ["pork belly", "tamarind broth", "spring roll wrappers", "ube halaya"]
            forbidden_ingredients = ["rosemary", "white wine", "pizza dough", "mozzarella"]
            
            state["found_correct_ingredients"] = all(ing in content_lower for ing in required_ingredients) and \
                                                 all(ing not in content_lower for ing in forbidden_ingredients)

    # Check for skill interaction in the trace would be in verify_prompt, 
    # but we can check if the agent at least attempted to read the CSV
    state_file = os.path.join(workspace, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
