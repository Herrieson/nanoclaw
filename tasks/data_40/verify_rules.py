import os
import json
import re

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "summary_report.txt")
    
    state = {
        "report_exists": False,
        "premium_discrepancy_correct": False,
        "deck_cost_correct": False,
        "extracted_numbers": []
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r") as f:
            content = f.read()
            
            # Find all numbers in the report (floats)
            numbers = re.findall(r'\d+\.\d+', content)
            state["extracted_numbers"] = numbers
            
            # Expected values:
            # Premium Sold: 20.5 + 15.0 + 40.0 = 75.5
            # Premium Delivered: 100.0
            # Discrepancy: 100.0 - 75.5 = 24.5
            # Deck Cost: 250.75 + 15.50 + 89.99 + 1.50 = 357.74
            
            if "24.5" in numbers or "24.50" in numbers:
                state["premium_discrepancy_correct"] = True
                
            if "357.74" in numbers:
                state["deck_cost_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)
        
    print(json.dumps(state))

if __name__ == "__main__":
    verify()
