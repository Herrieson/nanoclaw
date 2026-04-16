import os
import json
import re

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "My_Favorites.md")
    
    state = {
        "file_exists": False,
        "contains_peach": False,
        "contains_brisket": False,
        "contains_salad": False,
        "contains_ham": False,
        "excludes_bad_chicken": True,
        "excludes_bad_sardine": True,
        "excludes_bad_toast": True,
        "has_ingredients": False,
        "raw_content": ""
    }
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read()
            state["raw_content"] = content
            content_lower = content.lower()
            
            # Check for Target Titles
            if "peach cobbler" in content_lower:
                state["contains_peach"] = True
            if "gummy bear brisket" in content_lower:
                state["contains_brisket"] = True
            if "watermelon rind" in content_lower:
                state["contains_salad"] = True
            if "cola glazed ham" in content_lower:
                state["contains_ham"] = True
                
            # Check for Distractor Titles
            if "boiled chicken" in content_lower:
                state["excludes_bad_chicken"] = False
            if "sardine smoothie" in content_lower:
                state["excludes_bad_sardine"] = False
            if "plain toast" in content_lower:
                state["excludes_bad_toast"] = False
                
            # Check for ingredients presence (just checking a few key ingredients to ensure they were extracted)
            if "jalapeno" in content_lower and "pop rocks" in content_lower:
                state["has_ingredients"] = True

    # Output structural result
    with open(os.path.join(workspace_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
