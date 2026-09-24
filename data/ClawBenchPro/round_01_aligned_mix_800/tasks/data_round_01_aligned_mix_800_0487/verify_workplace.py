import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

# Configuration for LLM Judge
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def calculate_ground_truth(workspace):
    # 1. Get Policy (15% for Liberal Arts)
    policy_path = os.path.join(workspace, "governance/policies/signed_decree_nov12.json")
    with open(policy_path, 'r') as f:
        policy = json.load(f)
    cap = policy["department_caps"]["Liberal Arts"]["admin_cap_pct"] / 100.0

    # 2. Get Active Liberal Arts IDs and Map
    active_la = {}
    hr_path = os.path.join(workspace, "hr_data/active_personnel.csv")
    with open(hr_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Department'] == "Liberal Arts":
                active_la[row['EmpID']] = row['FullName']

    # 3. Aggregate Timesheets
    stats = {eid: {"total": 0.0, "admin": 0.0} for eid in active_la}
    ts_files = glob.glob(os.path.join(workspace, "timesheets/week_*/*.json"))
    
    for fpath in ts_files:
        with open(fpath, 'r') as f:
            data = json.load(f)
            eid = data['emp_id']
            if eid not in active_la:
                continue
            for entry in data['entries']:
                # Handle units
                duration = 0.0
                if "duration_minutes" in entry:
                    duration = float(entry["duration_minutes"])
                elif "duration_hours" in entry:
                    duration = float(entry["duration_hours"]) * 60.0
                
                stats[eid]["total"] += duration
                if entry["activity"] == "Admin":
                    stats[eid]["admin"] += duration

    violators = []
    for eid, data in stats.items():
        if data["total"] > 0:
            ratio = data["admin"] / data["total"]
            if ratio > cap:
                violators.append(active_la[eid])
    return sorted(violators)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. Check Directory and Files Existence (10 points)
    deliv_dir = os.path.join(workspace, "deliverables")
    violators_path = os.path.join(deliv_dir, "violators.json")
    memo_path = os.path.join(deliv_dir, "memo.md")
    
    if os.path.exists(deliv_dir) and os.path.isdir(deliv_dir):
        score += 5
        details.append({"item": "Deliverables directory exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Deliverables directory exists", "score": 0, "max_score": 5, "passed": False})

    # 2. Check violators.json format and content (60 points)
    if os.path.exists(violators_path):
        try:
            with open(violators_path, 'r') as f:
                agent_violators = json.load(f)
            
            if isinstance(agent_violators, list) and all(isinstance(x, str) for x in agent_violators):
                score += 10
                details.append({"item": "violators.json is valid JSON array of strings", "score": 10, "max_score": 10, "passed": True})
                
                # Logic Comparison
                gt_violators = calculate_ground_truth(workspace)
                agent_set = set(agent_violators)
                gt_set = set(gt_violators)
                
                if agent_set == gt_set:
                    score += 50
                    details.append({"item": "Violators list is perfectly accurate", "score": 50, "max_score": 50, "passed": True})
                else:
                    # Partial credit for overlap
                    intersection = agent_set.intersection(gt_set)
                    extra = agent_set - gt_set
                    missing = gt_set - agent_set
                    partial = max(0, (len(intersection) - len(extra)) / len(gt_set) * 50) if gt_set else 0
                    score += int(partial)
                    details.append({"item": "Violators list accuracy (partial)", "score": int(partial), "max_score": 50, "passed": False, 
                                    "reason": f"Missing: {list(missing)}, Extra: {list(extra)}"})
            else:
                details.append({"item": "violators.json format error", "score": 0, "max_score": 60, "passed": False})
        except Exception as e:
            details.append({"item": "Error reading violators.json", "score": 0, "max_score": 60, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "violators.json exists", "score": 0, "max_score": 60, "passed": False})

    # 3. Check memo.md with LLM (30 points)
    if os.path.exists(memo_path):
        with open(memo_path, 'r') as f:
            memo_content = f.read()
        
        # Tone and Content check
        is_professional = llm_judge_content("Is this memo addressed to the Liberal Arts department head and does it maintain a professional but firm/strict tone regarding administrative inefficiencies?", memo_content)
        mentions_policy = llm_judge_content("Does the memo explicitly or implicitly reference the violation of policy/caps regarding administrative time?", memo_content)
        
        if is_professional:
            score += 15
            details.append({"item": "Memo tone is professional and firm", "score": 15, "max_score": 15, "passed": True})
        else:
            details.append({"item": "Memo tone check", "score": 0, "max_score": 15, "passed": False, "reason": "LLM judged tone as inappropriate or missing recipient"})
            
        if mentions_policy:
            score += 15
            details.append({"item": "Memo content addresses policy violations", "score": 15, "max_score": 15, "passed": True})
        else:
            details.append({"item": "Memo content check", "score": 0, "max_score": 15, "passed": False, "reason": "LLM judged content as not addressing the core issue"})
    else:
        details.append({"item": "memo.md exists", "score": 0, "max_score": 30, "passed": False})

    # Output results
    results = {"total_score": min(100, score), "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
