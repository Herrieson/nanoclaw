import os
import json

def verify():
    state = {
        "exhibition_folder_exists": False,
        "inventory_file_exists": False,
        "correct_paintings_included": False,
        "sold_gifted_excluded": False,
        "total_value_correct": False
    }

    if os.path.isdir("exhibition"):
        state["exhibition_folder_exists"] = True

    file_path = "exhibition/gallery_inventory.md"
    if os.path.exists(file_path):
        state["inventory_file_exists"] = True
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # Check if all available paintings are in the file
            required_paintings = ["sunflowers", "spring morning", "morning dew", "abstract 1"]
            if all(p in content for p in required_paintings):
                state["correct_paintings_included"] = True
                
            # Check if sold/gifted paintings are properly excluded
            excluded_paintings = ["portrait of john", "sunset"]
            if not any(p in content for p in excluded_paintings):
                state["sold_gifted_excluded"] = True
                
            # Total value should be 500 + 250 + 200 + 600 = 1550
            if "1550" in content or "1,550" in content:
                state["total_value_correct"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
