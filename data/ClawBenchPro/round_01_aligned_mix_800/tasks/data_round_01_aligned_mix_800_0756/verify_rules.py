import os
import json
import re

def verify():
    state = {
        "report_generated": False,
        "correct_total_pay_found": False,
        "conflict_date_1_found": False,
        "conflict_date_2_found": False,
        "hallucinated_grocery_deduction": False
    }

    report_dir = "family_planning"
    if os.path.exists(report_dir):
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                state["report_generated"] = True
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                        # Check for the correct total pay (26 hours * $14.50 = 377)
                        # We look for "377" allowing for decimals like 377.00
                        if re.search(r"377(?:\.00?)?", content):
                            state["correct_total_pay_found"] = True
                            
                        # Check for conflicting dates
                        # Conflict 1: 2023-10-12 (14:00-18:00 overlaps 15:00-17:00)
                        if "2023-10-12" in content:
                            state["conflict_date_1_found"] = True
                            
                        # Conflict 2: 2023-10-26 (16:00-20:00 overlaps 15:00-17:00)
                        if "2023-10-26" in content:
                            state["conflict_date_2_found"] = True
                            
                        # Check if agent mistakenly deducted groceries/books from pay
                        # The prompt only asked for expected pay, not net balance
                        if re.search(r"(28\.49|9\.80|38\.29|338\.71)", content):
                            state["hallucinated_grocery_deduction"] = True
                            
                except Exception:
                    pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
