import os
import json
import sys

def verify():
    # Workspace defaults to current dir unless provided as arg
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "found_unapproved_servers": False,
        "found_correct_ingredients": False,
        "excluded_wrong_ingredients": False
    }
    
    deliverables_path = os.path.join(workspace, "deliverables")
    
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        # Check if there is at least one file generated
        report_files = [f for f in os.listdir(deliverables_path) if os.path.isfile(os.path.join(deliverables_path, f))]
        
        if report_files:
            state["report_file_exists"] = True
            
            # Read everything created in the deliverables dir
            combined_content = ""
            for rf in report_files:
                try:
                    with open(os.path.join(deliverables_path, rf), "r", encoding="utf-8") as f:
                        combined_content += f.read() + " "
                except Exception:
                    pass
            
            content_lower = combined_content.lower()
            
            # 1. Check for unapproved serving volunteers
            unapproved_names = ["mark reyes", "pedro cruz", "sarah jenkins"]
            state["found_unapproved_servers"] = all(name in content_lower for name in unapproved_names)
            
            # 2. Check for traditional Filipino ingredients
            filipino_ingredients = [
                "pork belly", "soy sauce", "vinegar", "garlic", "bay leaves", "black peppercorns",
                "pork ribs", "tamarind broth", "eggplant", "radish", "water spinach", "tomatoes",
                "ground pork", "carrots", "onions", "spring roll wrappers",
                "shaved ice", "evaporated milk", "ube halaya", "leche flan", "sweetened beans"
            ]
            
            found_count = sum(1 for ing in filipino_ingredients if ing in content_lower)
            # Acceptable threshold (at least ~70% extracted to account for minor variations in concatenation/formatting)
            if found_count >= 15:
                state["found_correct_ingredients"] = True
                
            # 3. Ensure no ingredients from non-Filipino recipes leaked in
            wrong_ingredients = ["macaroni", "cheddar cheese", "pasta", "tomato sauce"]
            found_wrong = sum(1 for wing in wrong_ingredients if wing in content_lower)
            
            if found_wrong == 0:
                state["excluded_wrong_ingredients"] = True

    # Output strict physical observation to state.json
    state_file = os.path.join(workspace, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
