import os
import json

def verify():
    verdict_path = "verdict.json"
    result = {
        "verdict_file_exists": False,
        "json_valid": False,
        "total_claimed_correct": False,
        "total_approved_correct": False,
        "denied_invoices_correct": False,
        "details": {}
    }

    if os.path.exists(verdict_path):
        result["verdict_file_exists"] = True
        try:
            with open(verdict_path, "r") as f:
                data = json.load(f)
            result["json_valid"] = True
            
            # Expected values based on env_builder:
            # Total claimed: 2500.00 + 850.50 + 120.25 + 400.00 + 1500.00 + 600.75 = 5971.50
            # Denied IDs: 
            # 2 (date < 10-15 and Dr. Smith)
            # 4 (Dr. Smith)
            # 5 (date < 10-15)
            # Denied: [2, 4, 5]
            # Approved IDs: 1, 3, 6
            # Total approved: 2500.00 + 120.25 + 600.75 = 3221.00
            
            claimed = float(data.get("total_claimed", 0))
            approved = float(data.get("total_approved", 0))
            denied = data.get("denied_invoices", [])
            
            if isinstance(denied, list):
                denied = sorted([int(x) for x in denied])
            
            result["details"]["agent_claimed"] = claimed
            result["details"]["agent_approved"] = approved
            result["details"]["agent_denied"] = denied
            
            if abs(claimed - 5971.50) < 0.01:
                result["total_claimed_correct"] = True
                
            if abs(approved - 3221.00) < 0.01:
                result["total_approved_correct"] = True
                
            if denied == [2, 4, 5]:
                result["denied_invoices_correct"] = True
                
        except Exception as e:
            result["details"]["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
