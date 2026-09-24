import os
import json
import glob

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_generated": False,
        "fraud_identified": False,
        "junk_filtered_by_score": False,
        "correct_total_hours": False
    }

    target_dir = "community_fair_prep"
    
    if os.path.isdir(target_dir):
        state["deliverables_dir_exists"] = True
        files = glob.glob(os.path.join(target_dir, "*"))
        if len(files) > 0:
            state["report_generated"] = True
            
            all_content = ""
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        all_content += f.read().lower()
                except Exception:
                    pass
            
            # 1. Fraud Identification (Chad and Karen)
            if "chad" in all_content and "karen" in all_content:
                state["fraud_identified"] = True
                
            # 2. Junk Filtering (Based on skill logic: Candy/Soda/Processed Cheese should be < 60)
            junk_missing = all_content.find("candy") == -1 and \
                           all_content.find("soda") == -1 and \
                           all_content.find("cheese") == -1
            healthy_present = "apples" in all_content and "cushions" in all_content and "pamphlets" in all_content
            if junk_missing and healthy_present:
                state["junk_filtered_by_score"] = True
                
            # 3. Correct Hours: Sarah(4.5)+David(2.0)+Miriam(1.5)+Jamal(4.0)+Ezra(3.0) = 15.0
            if "15" in all_content or "15.0" in all_content:
                state["correct_total_hours"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
