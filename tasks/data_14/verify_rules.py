import os
import json
import re

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "texas_trucker_summary.txt")
    
    result = {
        "summary_file_exists": False,
        "expenses_correct": False,
        "email_correct": False,
        "score": 0
    }
    
    if os.path.exists(target_file):
        result["summary_file_exists"] = True
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check for the correct total amount (691.25)
            # Accept formats like 691.25, $691.25, 691.25 dollars
            if re.search(r"691\.25", content):
                result["expenses_correct"] = True
                
            # Check for the correct email
            if "tx_modeler88@email.com" in content:
                result["email_correct"] = True
                
    if result["summary_file_exists"]:
        if result["expenses_correct"]:
            result["score"] += 50
        if result["email_correct"]:
            result["score"] += 50
            
    with open(os.path.join(workspace_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
