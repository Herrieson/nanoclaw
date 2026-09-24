import os
import sys
import json
import csv
import glob

def calculate_ground_truth(workspace):
    # This logic replicates the env_builder's logic to find the exact ground truth
    # 1. Resolve Project ID
    # Park Cleanup: PRJ-CP-044
    target_project_id = "PRJ-CP-044"
    
    # 2. Get Corp Name Mapping
    corp_map = {}
    registry_path = os.path.join(workspace, "campaign_mess/registry/corp_registry_master.json")
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            corps = json.load(f)
            for c in corps:
                corp_map[c['corp_id']] = c['business_name']
                
    # 3. Calculate Flaky Businesses (Park Cleanup & PENDING)
    flaky_ids = set()
    pledge_files = glob.glob(os.path.join(workspace, "campaign_mess/pledges/**/*.csv"), recursive=True)
    for pf in pledge_files:
        with open(pf, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['project_id'] == target_project_id and row['status'] == "PENDING":
                    flaky_ids.add(row['corp_id'])
    
    flaky_names = sorted([corp_map[cid] for cid in flaky_ids if cid in corp_map])
    
    # 4. Calculate Total Hours (Park Cleanup & APPROVED & Minutes -> Hours)
    total_minutes = 0
    ts_files = glob.glob(os.path.join(workspace, "campaign_mess/timesheets/**/*.json"), recursive=True)
    for tf in ts_files:
        with open(tf, 'r') as f:
            data = json.load(f)
            if data['project_id'] == target_project_id and data['approval_status'] == "APPROVED":
                total_minutes += data['minutes_logged']
    
    total_hours = float(total_minutes) / 60.0
    return flaky_names, total_hours

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables/report.json")
    
    score = 0
    details = []
    
    # 1. Directory Structure (10 points)
    if os.path.exists(os.path.join(workspace, "deliverables")):
        score += 5
        details.append({"item": "Directory deliverables exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Directory deliverables exists", "score": 0, "max_score": 5, "passed": False})
        
    if os.path.exists(report_path):
        score += 5
        details.append({"item": "File report.json exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "File report.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "Output file not found."})
        # If report doesn't exist, we skip content checks
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # 2. Schema and Format (10 points)
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        required_keys = ["flaky_businesses", "total_park_cleanup_hours"]
        if all(k in data for k in required_keys):
            score += 10
            details.append({"item": "JSON format and keys validation", "score": 10, "max_score": 10, "passed": True})
        else:
            details.append({"item": "JSON format and keys validation", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required keys"})
            data = {} # prevent crash
    except Exception as e:
        details.append({"item": "JSON parsing", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        data = {}

    # 3. Data Integrity & Accuracy (80 points)
    truth_flaky, truth_hours = calculate_ground_truth(workspace)
    
    # Part A: Flaky Businesses (40 points)
    agent_flaky = data.get("flaky_businesses", [])
    if isinstance(agent_flaky, list):
        agent_flaky_set = set(agent_flaky)
        truth_flaky_set = set(truth_flaky)
        
        if agent_flaky_set == truth_flaky_set:
            score += 40
            details.append({"item": "Flaky businesses accuracy", "score": 40, "max_score": 40, "passed": True})
        elif agent_flaky_set.issubset(truth_flaky_set) and len(agent_flaky_set) > 0:
            score += 20
            details.append({"item": "Flaky businesses accuracy", "score": 20, "max_score": 40, "passed": False, "reason": "Partial match, missing some businesses"})
        else:
            details.append({"item": "Flaky businesses accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect list. Expected {truth_flaky}"})
    else:
        details.append({"item": "Flaky businesses data type", "score": 0, "max_score": 40, "passed": False, "reason": "flaky_businesses is not a list"})

    # Part B: Total Hours (40 points)
    agent_hours = data.get("total_park_cleanup_hours", -1)
    if isinstance(agent_hours, (int, float)):
        # Check with a small epsilon for floating point issues
        if abs(float(agent_hours) - truth_hours) < 0.001:
            score += 40
            details.append({"item": "Total hours accuracy", "score": 40, "max_score": 40, "passed": True})
        else:
            # Check if they forgot the 60 conversion (minutes instead of hours)
            if abs(float(agent_hours) - (truth_hours * 60)) < 0.001:
                score += 10
                details.append({"item": "Total hours accuracy", "score": 10, "max_score": 40, "passed": False, "reason": "Calculated minutes instead of hours"})
            else:
                details.append({"item": "Total hours accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect calculation. Expected {truth_hours}"})
    else:
        details.append({"item": "Total hours data type", "score": 0, "max_score": 40, "passed": False, "reason": "total_park_cleanup_hours is not a number"})

    # Final Output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f)

if __name__ == "__main__":
    verify()
