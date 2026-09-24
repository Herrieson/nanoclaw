import os
import json
import csv

def verify():
    state = {
        "for_sale_dir_exists": False,
        "catalog_json_exists": False,
        "summary_txt_exists": False,
        "duplicates_removed_correctly": False,
        "low_condition_filtered": False,
        "missing_value_filtered": False,
        "total_value_correct": False,
        "count_correct": False
    }

    # 1. Check directory and files
    if os.path.exists("for_sale"):
        state["for_sale_dir_exists"] = True
        if os.path.exists("for_sale/catalog.json"):
            state["catalog_json_exists"] = True
        if os.path.exists("for_sale/summary.txt"):
            state["summary_txt_exists"] = True

    # 2. Logic Verification
    # Target Data:
    # Spider-Man 129: Keep 9.2 score ($2500)
    # X-Men 1: Removed (4.5 < 6.0)
    # Batman 181: Keep ($1500)
    # Fantastic Four 48: Removed (Missing Value)
    # Avengers 4: Keep ($3000)
    # Iron Man 1: Keep ($5000)
    # Green Lantern 76: Keep ($800)
    # X-Men 101: Removed (5.5 < 6.0)
    # Action Comics 252: Keep ($4500)
    
    # Expected Catalog: Iron Man 1 ($5000), Action Comics 252 ($4500), Avengers 4 ($3000), Spider-Man 129 ($2500), Batman 181 ($1500), Green Lantern 76 ($800)
    # Total Value: 5000+4500+3000+2500+1500+800 = 17300
    # Total Count: 6

    if state["catalog_json_exists"]:
        try:
            with open("for_sale/catalog.json", "r") as f:
                data = json.load(f)
                titles = [item["Title"] for item in data]
                values = [float(item["Market_Value"]) for item in data]
                scores = [float(item["Condition_Score"]) for item in data]
                
                state["duplicates_removed_correctly"] = ("The Amazing Spider-Man" in titles and titles.count("The Amazing Spider-Man") == 1 and 2500 in values)
                state["low_condition_filtered"] = all(s >= 6.0 for s in scores)
                state["missing_value_filtered"] = ("Fantastic Four" not in titles)
                state["count_correct"] = (len(data) == 6)
        except:
            pass

    if state["summary_txt_exists"]:
        try:
            with open("for_sale/summary.txt", "r") as f:
                content = f.read()
                if "17300" in content or "17,300" in content:
                    state["total_value_correct"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
