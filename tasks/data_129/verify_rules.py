import os
import json
import re

def verify():
    result = {
        "damaged_report_created": False,
        "damaged_item_correct": False,
        "damaged_count_correct": False,
        "extra_shift_created": False,
        "extra_shift_person_correct": False,
        "score": 0
    }
    
    # Note: total A123 Damaged count:
    # CSV: 2
    # JSON: 2
    # TXT: 2 ("Damaged again", "another A123 is Damaged")
    # MD: 1 ("all these A123 units being Damaged. (Found one more just now!)")
    # Total A123 = 7
    
    # Extra shifts:
    # Sarah: CSV(1), JSON(1), TXT(1), MD(1) = 4
    # David: JSON(1), MD(1) = 2
    # Winner: Sarah
    
    damaged_file = "damaged_report.txt"
    shift_file = "extra_shift.txt"
    
    if os.path.exists(damaged_file):
        result["damaged_report_created"] = True
        with open(damaged_file, "r") as f:
            content = f.read().lower()
            if "a123" in content:
                result["damaged_item_correct"] = True
            if "7" in content:
                result["damaged_count_correct"] = True
                
    if os.path.exists(shift_file):
        result["extra_shift_created"] = True
        with open(shift_file, "r") as f:
            content = f.read().lower()
            if "sarah" in content and "david" not in content:
                result["extra_shift_person_correct"] = True
            elif "sarah" in content:
                # If they included both but Sarah is clearly indicated as the winner, we give partial/full based on prompt later.
                # For strict rule:
                result["extra_shift_person_correct"] = True
                
    # Calculate crude score
    score = 0
    if result["damaged_report_created"]: score += 10
    if result["damaged_item_correct"]: score += 30
    if result["damaged_count_correct"]: score += 20
    if result["extra_shift_created"]: score += 10
    if result["extra_shift_person_correct"]: score += 30
    
    result["score"] = score
    
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
