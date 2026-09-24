import os
import sys
import json
import glob
from collections import defaultdict

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # ---------------- 1. 重新计算标准答案 ----------------
    approved_plates = set()
    correct_cuisine_counts = defaultdict(int)
    
    vendors_path = os.path.join(workspace, "archives", "vendors", "*.json")
    for filepath in glob.glob(vendors_path):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data.get("status") == "approved" and data.get("valid_until", "") >= "2024-10-27":
                    approved_plates.add(data.get("license_plate"))
                    correct_cuisine_counts[data.get("cuisine_type")] += 1
        except Exception:
            pass
            
    correct_cuisine_counts = dict(correct_cuisine_counts)
    
    today_entry_plates = set()
    logs_path = os.path.join(workspace, "logs", "gate_syslog", "*.log")
    for filepath in glob.glob(logs_path):
        # 只需要看2024-10-27的日志
        if "2024-10-27" not in filepath:
            continue
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if "[2024-10-27 " in line and "Action=ENTRY" in line:
                        # 提取 Plate
                        parts = line.strip().split()
                        for p in parts:
                            if p.startswith("Plate="):
                                plate_val = p.split("=")[1]
                                today_entry_plates.add(plate_val)
        except Exception:
            pass
            
    correct_unauthorized_plates = sorted(list(today_entry_plates - approved_plates))

    # ---------------- 2. 验证交付物 ----------------
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_file = os.path.join(deliverables_dir, "festival_report.json")
    
    # Check 1: deliverables directory
    if os.path.isdir(deliverables_dir):
        total_score += 10
        score_details.append({"item": "Deliverables directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'deliverables' exists."})
    else:
        score_details.append({"item": "Deliverables directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' is missing."})
        
    # Check 2: festival_report.json exists & valid
    agent_data = None
    if os.path.isfile(report_file):
        try:
            with open(report_file, 'r') as f:
                agent_data = json.load(f)
            total_score += 15
            score_details.append({"item": "Report file exists and is valid JSON", "score": 15, "max_score": 15, "passed": True, "reason": "festival_report.json is valid."})
        except Exception:
            score_details.append({"item": "Report file exists and is valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": "festival_report.json exists but is not valid JSON."})
    else:
        score_details.append({"item": "Report file exists and is valid JSON", "score": 0, "max_score": 15, "passed": False, "reason": "festival_report.json is missing."})
        
    # Check 3 & 4: Payload accuracy
    if agent_data and isinstance(agent_data, dict):
        agent_unauthorized = agent_data.get("unauthorized_plates", [])
        agent_cuisines = agent_data.get("cuisine_counts", {})
        
        # Check unauthorized_plates (45 points)
        if not isinstance(agent_unauthorized, list):
            score_details.append({"item": "Unauthorized plates format", "score": 0, "max_score": 45, "passed": False, "reason": "Key 'unauthorized_plates' is missing or not a list."})
        else:
            if agent_unauthorized == correct_unauthorized_plates:
                total_score += 45
                score_details.append({"item": "Unauthorized plates completely accurate", "score": 45, "max_score": 45, "passed": True, "reason": "The list matches standard answer exactly."})
            else:
                agent_set = set(agent_unauthorized)
                truth_set = set(correct_unauthorized_plates)
                intersection = agent_set.intersection(truth_set)
                
                # Penalty for fabricated entries
                false_positives = agent_set - truth_set
                
                if len(truth_set) > 0:
                    base_score = int(45 * (len(intersection) / len(truth_set)))
                else:
                    base_score = 0 if len(agent_set) > 0 else 45
                    
                final_unauth_score = max(0, base_score - (len(false_positives) * 2))
                
                total_score += final_unauth_score
                score_details.append({"item": "Unauthorized plates accuracy", "score": final_unauth_score, "max_score": 45, "passed": final_unauth_score == 45, "reason": f"Matched {len(intersection)}/{len(truth_set)}, false positives: {len(false_positives)}."})

        # Check cuisine_counts (30 points)
        if not isinstance(agent_cuisines, dict):
            score_details.append({"item": "Cuisine counts format", "score": 0, "max_score": 30, "passed": False, "reason": "Key 'cuisine_counts' is missing or not a dict."})
        else:
            if agent_cuisines == correct_cuisine_counts:
                total_score += 30
                score_details.append({"item": "Cuisine counts completely accurate", "score": 30, "max_score": 30, "passed": True, "reason": "The cuisine counts match standard answer exactly."})
            else:
                correct_keys = 0
                for k, v in correct_cuisine_counts.items():
                    if agent_cuisines.get(k) == v:
                        correct_keys += 1
                
                cuisine_score = int(30 * (correct_keys / max(1, len(correct_cuisine_counts))))
                total_score += cuisine_score
                score_details.append({"item": "Cuisine counts accuracy", "score": cuisine_score, "max_score": 30, "passed": cuisine_score == 30, "reason": f"Matched {correct_keys}/{len(correct_cuisine_counts)} cuisine types perfectly."})
    else:
        if agent_data is not None:
            score_details.append({"item": "Payload keys check", "score": 0, "max_score": 75, "passed": False, "reason": "JSON root is not a dict."})

    # Output score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
