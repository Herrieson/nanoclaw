import os
import json
import re

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "investment_summary.md")
    
    result = {
        "file_exists": False,
        "metrics_found": {},
        "is_correct": False,
        "error": None
    }
    
    if not os.path.exists(target_file):
        result["error"] = "investment_summary.md not found in the workspace."
        return result
        
    result["file_exists"] = True
    
    try:
        with open(target_file, "r") as f:
            content = f.read()
            
        # Extract table rows
        rows = re.findall(r'\|(.*?)\|(.*?)\|', content)
        for row in rows:
            key = row[0].strip().lower()
            val_str = row[1].strip()
            
            # Extract numbers from the value string
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
            if nums:
                val = float(nums[0])
                if "revenue" in key:
                    result["metrics_found"]["total_revenue"] = val
                elif "arpu" in key:
                    result["metrics_found"]["arpu"] = val
                elif "churn" in key:
                    result["metrics_found"]["churn_rate"] = val

        # Expected values:
        # Total Revenue = 50+50+50+50+100+50+50+80+15+5 = 500
        # Total Users = 10
        # ARPU = 500 / 10 = 50
        # Terminated Users = U02, U05 = 2
        # Churn Rate = 2 / 10 = 20 (or 0.2, we will accept either format if it parses to 20 or 0.2)
        
        rev_correct = result["metrics_found"].get("total_revenue") == 500.0
        arpu_correct = result["metrics_found"].get("arpu") == 50.0
        
        churn_val = result["metrics_found"].get("churn_rate")
        churn_correct = churn_val == 20.0 or churn_val == 0.2
        
        result["is_correct"] = rev_correct and arpu_correct and churn_correct
        
    except Exception as e:
        result["error"] = str(e)
        
    with open(os.path.join(workspace_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
