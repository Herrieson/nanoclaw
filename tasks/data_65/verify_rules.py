import os
import json
import re

def verify():
    base_dir = "."
    final_file = os.path.join(base_dir, "final_portfolio.txt")
    
    result = {
        "final_file_exists": False,
        "only_poems_included": False,
        "chronological_order": False,
        "corazon_replaced": False,
        "poems_count": 0
    }
    
    if os.path.exists(final_file):
        result["final_file_exists"] = True
        
        with open(final_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if diary entries are excluded
        if "Dear diary" not in content and "history essay" not in content:
            result["only_poems_included"] = True
            
        # Check replacements
        if "corazon" not in content.lower() and "heart" in content.lower():
            result["corazon_replaced"] = True
            
        # Find titles to check order and count
        titles = re.findall(r'Title:\s*(.+)', content)
        result["poems_count"] = len(titles)
        
        expected_order = ["The Autumn Leaves", "My Quiet Room", "Shadows on the Wall", "The Blank Page"]
        
        # Clean up titles for robust matching
        found_order = [t.strip() for t in titles]
        
        if found_order == expected_order:
            result["chronological_order"] = True

    # Output structural result
    state_file = os.path.join(base_dir, "verify_result.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    verify()
