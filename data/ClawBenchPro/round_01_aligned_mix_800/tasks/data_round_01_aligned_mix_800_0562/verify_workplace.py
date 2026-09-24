import os
import sys
import json
import csv
import re
from datetime import datetime

def calculate_hours_logic(in_time, out_time):
    fmt = "%H:%M"
    td = datetime.strptime(out_time, fmt) - datetime.strptime(in_time, fmt)
    return td.total_seconds() / 3600.0

def get_ground_truth(workspace):
    # 1. Load Roster
    roster = {}
    with open(os.path.join(workspace, 'db/roster.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            roster[row['StudentID']] = {
                'name': row['FullName'],
                'grade': row['GradeLevel']
            }

    # 2. Parse Logs for Last Status
    last_status = {}
    log_path = os.path.join(workspace, 'admin_records/slip_transactions.log')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if 'UPDATE: Record for' in line:
                    match = re.search(r'Record for (STU\d+) .* Status: (\w+)', line)
                    if match:
                        s_id, status = match.groups()
                        last_status[s_id] = status

    # 3. Parse Scans
    scan_dir = os.path.join(workspace, 'scans/checkins')
    student_hours = {}
    for filename in os.listdir(scan_dir):
        path = os.path.join(scan_dir, filename)
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                if data.get('location') == 'EcoPark':
                    for rec in data.get('records', []):
                        s_id = rec['id']
                        h = calculate_hours_logic(rec['in'], rec['out'])
                        student_hours[s_id] = student_hours.get(s_id, 0) + h
        except:
            continue # Skip corrupted

    # 4. Aggregations
    hours_by_grade = {}
    missing_slips = []
    
    for s_id, hours in student_hours.items():
        if hours <= 0: continue
        
        info = roster.get(s_id)
        if not info: continue
        
        # Hours by grade
        grade = info['grade']
        hours_by_grade[grade] = hours_by_grade.get(grade, 0) + hours
        
        # Missing slips logic
        status = last_status.get(s_id)
        if status != 'Signed':
            missing_slips.append(info['name'])
            
    return {
        "hours_by_grade": {k: round(v, 4) for k, v in hours_by_grade.items()},
        "missing_slips_participants": sorted(missing_slips)
    }

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "final_docs/report.json")
    
    score = 0
    details = []
    
    # 1. File existence
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Check report.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    else:
        details.append({"item": "Check report.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "report.json not found in final_docs/"})
        # If file doesn't exist, we stop or continue with zero for others
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. Content validation
    try:
        with open(report_path, 'r') as f:
            agent_data = json.load(f)
            
        gt = get_ground_truth(workspace)
        
        # Check keys
        required_keys = ["hours_by_grade", "missing_slips_participants"]
        keys_present = all(k in agent_data for k in required_keys)
        if keys_present:
            score += 10
            details.append({"item": "JSON keys validation", "score": 10, "max_score": 10, "passed": True, "reason": "Both required keys present"})
        else:
            details.append({"item": "JSON keys validation", "score": 0, "max_score": 10, "passed": False, "reason": "Missing keys in report.json"})

        # Check hours_by_grade (numeric match)
        gt_hours = gt["hours_by_grade"]
        ag_hours = agent_data.get("hours_by_grade", {})
        
        correct_grades = 0
        total_grades = len(gt_hours)
        for g, val in gt_hours.items():
            if g in ag_hours and abs(float(ag_hours[g]) - val) < 0.01:
                correct_grades += 1
        
        grade_score = int((correct_grades / total_grades) * 40) if total_grades > 0 else 40
        score += grade_score
        details.append({"item": "Hours by grade calculation", "score": grade_score, "max_score": 40, "passed": correct_grades == total_grades, "reason": f"Correctly calculated {correct_grades}/{total_grades} grades"})

        # Check missing_slips_participants (Alphabetical list match)
        gt_slips = gt["missing_slips_participants"]
        ag_slips = agent_data.get("missing_slips_participants", [])
        
        # Normalize and compare sets
        if sorted([str(s).strip() for s in ag_slips]) == gt_slips:
            score += 40
            details.append({"item": "Missing slips participants list", "score": 40, "max_score": 40, "passed": True, "reason": "List is perfectly accurate and sorted"})
        else:
            # Partial credit for overlap
            set_gt = set(gt_slips)
            set_ag = set(ag_slips)
            intersection = set_gt.intersection(set_ag)
            recall = len(intersection) / len(set_gt) if len(set_gt) > 0 else 0
            precision = len(intersection) / len(set_ag) if len(set_ag) > 0 else 0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            p_score = int(f1 * 30) # Max 30 for partial match, missing 10 for sorting or exactness
            score += p_score
            details.append({"item": "Missing slips participants list", "score": p_score, "max_score": 40, "passed": False, "reason": f"List mismatch. F1 score: {f1:.2f}. Ensure sorting and correct filtering of 'EcoPark' + 'Last status'."})

    except Exception as e:
        details.append({"item": "JSON content parsing", "score": 0, "max_score": 80, "passed": False, "reason": f"Error parsing JSON content: {str(e)}"})

    # Final score cap
    final_score = min(max(int(score), 0), 100)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": final_score, "details": details}, f)

if __name__ == "__main__":
    verify()
