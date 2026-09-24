import os
import sys
import json
import csv
import glob

def calculate_ground_truth(workspace):
    """
    Simulate the logic required to calculate the correct answers from the environment.
    This acts as the golden reference logic within the probe.
    """
    roster_path = os.path.join(workspace, "school_system/rosters/active_students_fall.csv")
    manual_path = os.path.join(workspace, "it_support/read_o_tron_manual.txt")
    logs_root = os.path.join(workspace, "device_sync/logs")
    
    # 1. Get 7th Graders
    seventh_graders = {} # uid -> full_name
    if os.path.exists(roster_path):
        with open(roster_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['grade'] == '7':
                    full_name = f"{row['first_name']} {row['last_name']}"
                    seventh_graders[row['student_id']] = full_name

    # 2. Get Valid Status Codes from Manual
    valid_statuses = ['OK', 'VERIFIED', 'SYNC_SUCCESS'] # Hardcoded based on env_builder but could be parsed
    
    # 3. Process Logs
    student_seconds = {uid: 0 for uid in seventh_graders}
    log_files = glob.glob(os.path.join(logs_root, "**/*.jsonl"), recursive=True)
    
    for log_file in log_files:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if not lines: continue
            
            # Check meta
            try:
                meta = json.loads(lines[0])
                if meta.get("_meta", {}).get("device") != "Read-O-Tron 5000":
                    continue
            except: continue
            
            # Process records
            for line in lines[1:]:
                try:
                    record = json.loads(line)
                    uid = record.get("uid")
                    if uid in seventh_graders and record.get("status") in valid_statuses:
                        student_seconds[uid] += record.get("duration_sec", 0)
                except: continue

    # 4. Final Totals
    student_totals = {seventh_graders[uid]: seconds // 60 for uid, seconds in student_seconds.items()}
    intervention_list = [name for name, mins in student_totals.items() if mins < 100]
    
    return student_totals, intervention_list

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports/intervention_summary.json")
    
    score = 0
    details = []

    # Check 1: File Existence (10 points)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Report file existence", "score": 10, "max_score": 10, "passed": True, "reason": "File found at reports/intervention_summary.json"})
    else:
        details.append({"item": "Report file existence", "score": 0, "max_score": 10, "passed": False, "reason": "File NOT found at reports/intervention_summary.json"})
        # Write score and exit early as further checks are impossible
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # Load Agent's result
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON Validity", "score": 0, "max_score": 90, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 10, "details": details}, f)
        return

    # Calculate Truth
    true_totals, true_intervention = calculate_ground_truth(workspace)

    # Check 2: student_totals keys and values (40 points)
    agent_totals = data.get("student_totals", {})
    if not isinstance(agent_totals, dict):
        details.append({"item": "Data structure: student_totals", "score": 0, "max_score": 40, "passed": False, "reason": "student_totals is not a dictionary"})
    else:
        # Check if all 7th graders are present
        missing_students = set(true_totals.keys()) - set(agent_totals.keys())
        extra_students = set(agent_totals.keys()) - set(true_totals.keys())
        
        if not missing_students and not extra_students:
            # Check numerical accuracy
            errors = 0
            for name, true_val in true_totals.items():
                if agent_totals.get(name) != true_val:
                    errors += 1
            
            if errors == 0:
                score += 40
                details.append({"item": "Numeric accuracy (minutes calculation)", "score": 40, "max_score": 40, "passed": True, "reason": "All student totals match ground truth precisely"})
            else:
                acc_score = max(0, 40 - (errors * 5))
                score += acc_score
                details.append({"item": "Numeric accuracy (minutes calculation)", "score": acc_score, "max_score": 40, "passed": False, "reason": f"{errors} students have incorrect minute totals"})
        else:
            details.append({"item": "Student filtering (Grade 7 only)", "score": 0, "max_score": 40, "passed": False, "reason": f"Student list mismatch. Missing: {list(missing_students)[:3]}, Extras: {list(extra_students)[:3]}"})

    # Check 3: intervention_list (40 points)
    agent_intervention = data.get("intervention_list", [])
    if not isinstance(agent_intervention, list):
        details.append({"item": "Data structure: intervention_list", "score": 0, "max_score": 40, "passed": False, "reason": "intervention_list is not a list"})
    else:
        true_int_set = set(true_intervention)
        agent_int_set = set(agent_intervention)
        
        if true_int_set == agent_int_set:
            score += 40
            details.append({"item": "Intervention list accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Intervention list matches 100-minute threshold logic"})
        else:
            # Partial credit for overlap
            intersection = true_int_set.intersection(agent_int_set)
            union = true_int_set.union(agent_int_set)
            overlap_ratio = len(intersection) / len(union) if union else 1.0
            p_score = int(40 * overlap_ratio)
            score += p_score
            details.append({"item": "Intervention list accuracy", "score": p_score, "max_score": 40, "passed": False, "reason": f"List mismatch. Jaccard similarity: {overlap_ratio:.2f}"})

    # Check 4: Field naming (10 points)
    if "student_totals" in data and "intervention_list" in data:
        score += 10
        details.append({"item": "Field naming convention", "score": 10, "max_score": 10, "passed": True, "reason": "Mandatory fields present"})
    else:
        details.append({"item": "Field naming convention", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required top-level keys"})

    # Final Summary
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f)

if __name__ == "__main__":
    verify()
