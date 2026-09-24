import os
import sys
import json
import csv
import yaml
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily data-driven)
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def calculate_ground_truth(workspace):
    """
    Re-implement the logic with fixed seed logic to get ground truth.
    Since random.seed(1588) was used in env_builder, the files are deterministic.
    """
    # 1. Get Active Provider
    with open(os.path.join(workspace, "system_config.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    active_provider = config["active_provider"]
    
    # 2. Get Whitelist
    whitelist_path = os.path.join(workspace, f"insurance_policies/{active_provider}/whitelist.json")
    with open(whitelist_path, 'r') as f:
        whitelist = set(json.load(f)["authorized_codes"])
    
    # 3. Process Raw Exports
    raw_dir = os.path.join(workspace, "raw_exports")
    valid_sessions = [] # List of tuples (Date, PatientName, ProcCode, DurationHours)
    unauthorized_patients = set()
    
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            if not file.endswith(".json"): continue
            with open(os.path.join(root, file), 'r') as f:
                try:
                    content = json.load(f)
                    if content.get("metadata", {}).get("status") != "FINAL":
                        continue
                    
                    for entry in content.get("data", []):
                        # Clean Name
                        raw_name = entry["PatientName"]
                        parts = [p.strip().capitalize() for p in raw_name.split(",")]
                        last = parts[0]
                        first_initial = parts[1][0].upper() if len(parts) > 1 and len(parts[1]) > 0 else "?"
                        clean_name = f"{last}, {first_initial}."
                        
                        # Clean Duration
                        raw_dur = str(entry["DurationHours"])
                        clean_dur = float(''.join(c for c in raw_dur if c.isdigit() or c == '.'))
                        
                        # Clean Code
                        clean_code = entry["ProcCode"].strip()
                        
                        record = (entry["Date"], clean_name, clean_code, clean_dur)
                        valid_sessions.append(record)
                except:
                    continue

    # Deduplicate
    deduplicated = list(set(valid_sessions))
    
    # Filter by Whitelist & Calculate Summary
    final_authorized = []
    total_hours = 0.0
    
    for row in deduplicated:
        if row[2] in whitelist:
            final_authorized.append(row)
            total_hours += row[3]
        else:
            unauthorized_patients.add(row[1])
            
    return final_authorized, total_hours, sorted(list(unauthorized_patients))

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = os.path.join(workspace, "billing_ready")
    csv_path = os.path.join(output_dir, "authorized_sessions.csv")
    json_path = os.path.join(output_dir, "summary.json")
    
    score = 0
    details = []

    # 1. Structural Checks (10 points)
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        score += 5
        details.append({"item": "Directory billing_ready exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Directory billing_ready exists", "score": 0, "max_score": 5, "passed": False})

    files_exist = os.path.exists(csv_path) and os.path.exists(json_path)
    if files_exist:
        score += 5
        details.append({"item": "Output files exist", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Output files exist", "score": 0, "max_score": 5, "passed": False})

    if not files_exist:
        # Cannot proceed with deep check if files are missing
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f)
        return

    # Generate Ground Truth
    gt_authorized, gt_hours, gt_unauth_pts = calculate_ground_truth(workspace)

    # 2. CSV Content Check (40 points)
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            # Check Headers
            expected_headers = ["Date", "PatientName", "ProcCode", "DurationHours"]
            if all(h in reader.fieldnames for h in expected_headers):
                score += 10
                details.append({"item": "CSV headers correct", "score": 10, "max_score": 10, "passed": True})
            else:
                details.append({"item": "CSV headers correct", "score": 0, "max_score": 10, "passed": False})

            agent_rows = []
            for r in reader:
                agent_rows.append((r["Date"], r["PatientName"], r["ProcCode"], float(r["DurationHours"])))
            
            # Use sets for comparison (order independent)
            agent_set = set(agent_rows)
            gt_set = set(gt_authorized)
            
            intersection = agent_set.intersection(gt_set)
            if len(gt_set) > 0:
                accuracy = len(intersection) / len(gt_set)
                penalty = max(0, len(agent_set) - len(gt_set)) / len(gt_set) # Penalty for noise
                csv_score = int(max(0, (accuracy - penalty) * 30))
                score += csv_score
                details.append({"item": "CSV content accuracy (Deduplication/Filtering/Cleaning)", "score": csv_score, "max_score": 30, "passed": csv_score > 20})
    except Exception as e:
        details.append({"item": "CSV content check failed", "score": 0, "max_score": 40, "passed": False, "reason": str(e)})

    # 3. Summary JSON Check (50 points)
    try:
        with open(json_path, 'r') as f:
            agent_summary = json.load(f)
            
            # Check Hours (Allow small float delta)
            agent_hours = agent_summary.get("total_billable_hours", 0)
            if abs(agent_hours - gt_hours) < 0.1:
                score += 25
                details.append({"item": "Total billable hours correct", "score": 25, "max_score": 25, "passed": True})
            else:
                details.append({"item": "Total billable hours correct", "score": 0, "max_score": 25, "passed": False, "reason": f"Expected {gt_hours}, got {agent_hours}"})
                
            # Check Unauthorized Patients
            agent_unauth = agent_summary.get("unauthorized_patients", [])
            if sorted(agent_unauth) == gt_unauth_pts:
                score += 25
                details.append({"item": "Unauthorized patients list correct", "score": 25, "max_score": 25, "passed": True})
            else:
                details.append({"item": "Unauthorized patients list correct", "score": 0, "max_score": 25, "passed": False, "reason": "List mismatch or formatting error"})
                
    except Exception as e:
        details.append({"item": "Summary JSON check failed", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f)

if __name__ == "__main__":
    verify()
