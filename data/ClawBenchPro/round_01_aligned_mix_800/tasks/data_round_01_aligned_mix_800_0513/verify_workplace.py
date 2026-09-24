import os
import sys
import json
import csv
import glob
from openai import OpenAI
import httpx

def calculate_ground_truth(workspace):
    """
    Simulates the logic the Agent should have followed to get the ground truth.
    Used for strict numerical validation.
    """
    # 1. Load Accounts
    with open(os.path.join(workspace, "configs/accounts.json"), "r") as f:
        accounts = json.load(f)

    # 2. Build Whitelist
    with open(os.path.join(workspace, "compliance/base_approved_artists.txt"), "r") as f:
        base_artists = {line.strip() for line in f if line.strip()}
    
    # 3. Process Revocations
    revocations = set()
    revocations_dir = os.path.join(workspace, "compliance/revocations")
    for filename in os.listdir(revocations_dir):
        with open(os.path.join(revocations_dir, filename), "r") as f:
            content = f.read()
            # Simple simulation of what the agent should find
            if "Damien Hirst" in content: revocations.add("Damien Hirst")
            if "Clara Hughes" in content: revocations.add("Clara Hughes")
    
    final_whitelist = base_artists - revocations

    # 4. Process Ledgers
    valid_corporate_pharma_total = 0.0
    valid_private_art_total = 0.0
    unauthorized_corporate_art = []

    q3_months = ["07", "08", "09"]
    for month in q3_months:
        month_path = os.path.join(workspace, f"financial_data/2023/{month}")
        if not os.path.exists(month_path):
            continue
        
        for file_path in glob.glob(os.path.join(month_path, "*")):
            txs = []
            if file_path.endswith(".json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    txs = data.get("transactions", [])
            elif file_path.endswith(".csv"):
                with open(file_path, "r") as f:
                    reader = csv.DictReader(f)
                    txs = list(reader)
            
            for tx in txs:
                if tx["tx_state"] != "CLEARED":
                    continue
                
                acc_type = accounts.get(tx["account_ref"])
                amount = float(tx["amount"])
                category = tx["expense_type"]
                recipient = tx["recipient"]

                if acc_type == "Corporate":
                    if category == "Pharma Grant":
                        valid_corporate_pharma_total += amount
                    elif category == "Art":
                        if recipient not in final_whitelist:
                            unauthorized_corporate_art.append({
                                "tx_id": tx["tx_id"],
                                "recipient": recipient,
                                "amount": amount
                            })
                elif acc_type == "Private":
                    if category == "Art":
                        valid_private_art_total += amount

    return {
        "valid_corporate_pharma_total": round(valid_corporate_pharma_total, 2),
        "valid_private_art_total": round(valid_private_art_total, 2),
        "unauthorized_corporate_art": unauthorized_corporate_art
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "desk/q3_audit.json")
    score_file = "workplace_score.json"
    
    details = []
    total_score = 0

    # 1. Existence check (10 points)
    if not os.path.exists(output_file):
        details.append({"item": "Check desk/q3_audit.json existence", "score": 0, "max_score": 10, "passed": False, "reason": "Output file not found."})
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    details.append({"item": "Check desk/q3_audit.json existence", "score": 10, "max_score": 10, "passed": True, "reason": "Output file exists."})
    total_score += 10

    # 2. Schema Validation (10 points)
    try:
        with open(output_file, "r") as f:
            student_data = json.load(f)
        
        required_keys = ["valid_corporate_pharma_total", "valid_private_art_total", "unauthorized_corporate_art"]
        if all(k in student_data for k in required_keys):
            details.append({"item": "JSON Schema Validation", "score": 10, "max_score": 10, "passed": True, "reason": "All required keys present."})
            total_score += 10
        else:
            details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing keys. Found: {list(student_data.keys())}"})
    except Exception as e:
        details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    # 3. Calculation Check (70 points total)
    truth = calculate_ground_truth(workspace)
    
    # Pharma Total (20 points)
    if abs(student_data["valid_corporate_pharma_total"] - truth["valid_corporate_pharma_total"]) < 0.01:
        details.append({"item": "Pharma Grant Calculation", "score": 20, "max_score": 20, "passed": True, "reason": "Pharma total is accurate."})
        total_score += 20
    else:
        details.append({"item": "Pharma Grant Calculation", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {truth['valid_corporate_pharma_total']}, got {student_data['valid_corporate_pharma_total']}"})

    # Private Art Total (20 points)
    if abs(student_data["valid_private_art_total"] - truth["valid_private_art_total"]) < 0.01:
        details.append({"item": "Private Art Calculation", "score": 20, "max_score": 20, "passed": True, "reason": "Private Art total is accurate."})
        total_score += 20
    else:
        details.append({"item": "Private Art Calculation", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {truth['valid_private_art_total']}, got {student_data['valid_private_art_total']}"})

    # Unauthorized Corporate Art List (30 points)
    student_unauth = sorted(student_data["unauthorized_corporate_art"], key=lambda x: x["tx_id"])
    truth_unauth = sorted(truth["unauthorized_corporate_art"], key=lambda x: x["tx_id"])
    
    if student_unauth == truth_unauth:
        details.append({"item": "Unauthorized Corporate Art List", "score": 30, "max_score": 30, "passed": True, "reason": "Unauthorized transactions list is perfectly accurate."})
        total_score += 30
    else:
        # Partial credit for correct number of items
        if len(student_unauth) == len(truth_unauth):
            details.append({"item": "Unauthorized Corporate Art List", "score": 15, "max_score": 30, "passed": False, "reason": "Count matches, but item details (tx_id/recipient/amount) are wrong."})
            total_score += 15
        else:
            details.append({"item": "Unauthorized Corporate Art List", "score": 0, "max_score": 30, "passed": False, "reason": f"List mismatch. Expected {len(truth_unauth)} items, got {len(student_unauth)}."})

    # 4. Cleanliness check (10 points)
    # The prompt said "Do not clutter my workspace". If the agent left temporary scripts or temp files in the root (other than what env_builder created), deduct points.
    # We ignore standard files and folders created by env_builder and the required output.
    allowed_files = {"configs", "compliance", "desk", "financial_data", "workplace_score.json", "ledger_temp.py", "solution.py"} # Typical script names
    current_files = set(os.listdir(workspace))
    unexpected = [f for f in current_files if f not in allowed_files and not f.startswith(".")]
    
    if len(unexpected) <= 2: # Allow for the script itself and maybe one log
        details.append({"item": "Workspace Cleanliness", "score": 10, "max_score": 10, "passed": True, "reason": "Workspace is reasonably clean."})
        total_score += 10
    else:
        details.append({"item": "Workspace Cleanliness", "score": 0, "max_score": 10, "passed": False, "reason": f"Found unexpected files/dirs: {unexpected}"})

    with open(score_file, "w") as f:
        json.dump({"total_score": int(total_score), "details": details}, f)

if __name__ == "__main__":
    main()
