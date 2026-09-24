import os
import json
import glob

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_generated": False,
        "uninvited_crashes_identified": False,
        "junk_food_filtered_out": False,
        "healthy_items_retained": False,
        "correct_valid_hours_calculated": False
    }

    target_dir = "community_fair_prep"
    
    if os.path.isdir(target_dir):
        state["deliverables_dir_exists"] = True
        files = glob.glob(os.path.join(target_dir, "*"))
        if len(files) > 0:
            state["report_generated"] = True
            
            # Read all generated content to evaluate logic
            all_content = ""
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        all_content += f.read().lower()
                except Exception:
                    pass
            
            # Check for uninvited guests identification (Chad and Karen)
            if "chad" in all_content and "karen" in all_content:
                state["uninvited_crashes_identified"] = True
                
            # Check for junk food filtering (Candy Bars, Soda Cans, Processed Cheese)
            if "candy" not in all_content and "soda" not in all_content and "processed cheese" not in all_content:
                state["junk_food_filtered_out"] = True
                
            # Check for retention of healthy/useful items
            if "apples" in all_content and "cushions" in all_content and "pamphlets" in all_content and "bread" in all_content:
                state["healthy_items_retained"] = True
                
            # Check correct valid hours calculated
            # Valid hours: Sarah (4.5) + David (2.0) + Jamal (4) + Miriam (1.5) = 12.0
            # Invalid (Chad 6, Karen 3.5) should be ignored.
            if "12" in all_content or "12.0" in all_content:
                state["correct_valid_hours_calculated"] = True

    # Write objective state to a physical state.json file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
