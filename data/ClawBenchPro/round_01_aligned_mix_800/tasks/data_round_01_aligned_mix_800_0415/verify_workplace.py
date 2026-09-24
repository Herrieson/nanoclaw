import os
import sys
import json
import csv
import glob

def calculate_ground_truth(workspace):
    """
    Replicate the logic from env_builder.py to find the absolute truth.
    This ensures that even though the environment is randomized, the validation is always correct.
    """
    # 1. Get Whitelist
    whitelist = set()
    v_json = os.path.join(workspace, "policy_vault/v2/config/vendor_access.json")
    v_txt = os.path.join(workspace, "policy_vault/v2/config/appendix_b.txt")
    
    if os.path.exists(v_json):
        with open(v_json, 'r') as f:
            data = json.load(f)
            whitelist.update([v.strip().lower() for v in data.get("approved", [])])
    
    if os.path.exists(v_txt):
        with open(v_txt, 'r') as f:
            lines = f.readlines()
            # Skip header "SUPPLEMENTARY APPROVED VENDORS:"
            for line in lines[1:]:
                if line.strip():
                    whitelist.add(line.strip().lower())

    # 2. Process Logs
    total_approved_sum = 0.0
    rogue_contractors = set()
    
    archive_root = os.path.join(workspace, "archive_root")
    for root, dirs, files in os.walk(archive_root):
        # Margaret's Rule: Ignore "temp", "corrupted", or "test" files/folders
        # Based on env_builder: is_valid = "temp" not in d and "backups" not in d
        path_parts = root.split(os.sep)
        if any(token in path_parts for token in ["temp", "backups", "corrupted", "test"]):
            continue
            
        for file in files:
            if not (file.endswith(".csv") or file.endswith(".json")):
                continue
            if "junk" in file:
                continue
                
            file_path = os.path.join(root, file)
            rows = []
            if file.endswith(".csv"):
                try:
                    with open(file_path, 'r') as f:
                        reader = csv.DictWriter(f, fieldnames=["date", "contractor", "amount"]) # For typing
                        reader = csv.DictReader(f)
                        rows = list(reader)
                except: continue
            else:
                try:
                    with open(file_path, 'r') as f:
                        rows = json.load(f)
                except: continue
            
            for row in rows:
                vendor_raw = row.get("contractor", "")
                vendor_clean = vendor_raw.strip().lower()
                amount = float(row.get("amount", 0))
                
                if vendor_clean in whitelist:
                    total_approved_sum += amount
                else:
                    # Based on logic: unique names, cleaned
                    rogue_contractors.add(vendor_clean)
                    
    return round(total_approved_sum, 2), sorted(list(rogue_contractors))

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables/audit_report.json")
    
    score = 0
    details = []

    # Ground Truth
    gt_cost, gt_rogues = calculate_ground_truth(workspace)

    # 1. File existence Check (10 points)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Report Existence", "score": 10, "max_score": 10, "passed": True, "reason": "audit_report.json found in deliverables."})
    else:
        details.append({"item": "Report Existence", "score": 0, "max_score": 10, "passed": False, "reason": "audit_report.json missing."})
        # If no file, write score and exit
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. JSON Schema Check (10 points)
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON Format", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
    except Exception as e:
        details.append({"item": "JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 3. Calculation Accuracy (40 points) - 5% tolerance for rounding or floating point issues
    agent_cost = data.get("total_approved_cost", -1)
    if abs(float(agent_cost) - gt_cost) < 0.01:
        score += 40
        details.append({"item": "Calculation Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": f"Cost {agent_cost} matches ground truth {gt_cost}."})
    elif abs(float(agent_cost) - gt_cost) < 1.0:
        score += 20
        details.append({"item": "Calculation Accuracy", "score": 20, "max_score": 40, "passed": False, "reason": f"Cost {agent_cost} is close but inaccurate. Truth: {gt_cost}."})
    else:
        details.append({"item": "Calculation Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Cost {agent_cost} is significantly different from truth {gt_cost}."})

    # 4. Rogue Contractor Identification (40 points)
    agent_rogues = [r.strip().lower() for r in data.get("unapproved_contractors", [])]
    agent_rogues_set = set(agent_rogues)
    gt_rogues_set = set(gt_rogues)
    
    intersection = agent_rogues_set.intersection(gt_rogues_set)
    if len(gt_rogues_set) > 0:
        recall = len(intersection) / len(gt_rogues_set)
        # Precision check: did they include valid vendors?
        extra = agent_rogues_set - gt_rogues_set
        
        rogue_score = int(recall * 40)
        if len(extra) > 0:
            penalty = min(rogue_score, 10)
            rogue_score -= penalty
            reason = f"Identified {len(intersection)}/{len(gt_rogues_set)} rogues but included {len(extra)} incorrect ones."
        else:
            reason = f"Successfully identified {len(intersection)}/{len(gt_rogues_set)} rogue contractors."
        
        score += rogue_score
        details.append({"item": "Rogue Identification", "score": rogue_score, "max_score": 40, "passed": recall > 0.9, "reason": reason})
    else:
        score += 40
        details.append({"item": "Rogue Identification", "score": 40, "max_score": 40, "passed": True, "reason": "No rogues existed and none reported."})

    # Final Output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f)

if __name__ == "__main__":
    verify()
