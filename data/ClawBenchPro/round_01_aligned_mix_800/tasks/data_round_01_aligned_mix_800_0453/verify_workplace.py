import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

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

def compute_gold_standard(workspace):
    # 1. Parse base roster
    roster_path = os.path.join(workspace, "administration/roster_v1.json")
    if not os.path.exists(roster_path):
        return 0, []
        
    with open(roster_path, 'r', encoding='utf-8') as f:
        roster = set(json.load(f))
        
    # 2. Apply amendments
    amendments_dir = os.path.join(workspace, "administration/amendments")
    if os.path.exists(amendments_dir):
        for fname in os.listdir(amendments_dir):
            if fname.endswith(".txt"):
                with open(os.path.join(amendments_dir, fname), 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("ADDED: "):
                            roster.add(line[7:].strip())
                        elif line.startswith("REMOVED: "):
                            name = line[9:].strip()
                            if name in roster:
                                roster.remove(name)
                                
    # 3. Parse logs
    logs_dir = os.path.join(workspace, "raw_logs")
    
    class State:
        total_hours = 0
        flagged = set()

    def process_row(student, hours, slip):
        try:
            hours = int(hours)
        except ValueError:
            return
        is_valid_slip = slip.lower().startswith('y')
        if student in roster and is_valid_slip:
            State.total_hours += hours
        else:
            State.flagged.add(student)

    if os.path.exists(logs_dir):
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace)
                
                # Filter noise based on path/filename
                if re.search(r'draft|backup|deprecated', rel_path, re.IGNORECASE):
                    continue
                    
                if file.endswith('.json'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for row in data:
                            process_row(row.get('student'), row.get('hours'), row.get('slip'))
                elif file.endswith('.csv'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            process_row(row.get('StudentName'), row.get('WorkedHours'), row.get('ParentSlipStatus'))
                elif file.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line: continue
                            parts = line.split('|')
                            if len(parts) == 3:
                                student = parts[0].split(':')[1].strip()
                                hours = parts[1].split(':')[1].strip()
                                slip = parts[2].split(':')[1].strip()
                                process_row(student, hours, slip)
                            
    return State.total_hours, sorted(list(State.flagged))

def verify(workspace):
    gold_total_hours, gold_flagged = compute_gold_standard(workspace)
    
    target_file = os.path.join(workspace, "deliverables", "final_report.json")
    
    details = []
    total_score = 0
    
    # Check 1: File existence and format (20 pts)
    agent_data = None
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            
            if isinstance(agent_data, dict) and "total_valid_hours" in agent_data and "flagged_students" in agent_data:
                details.append({"item": "Deliverable file exists and JSON schema is valid", "score": 20, "max_score": 20, "passed": True, "reason": "File exists with correct keys."})
                total_score += 20
            else:
                details.append({"item": "Deliverable file exists and JSON schema is valid", "score": 5, "max_score": 20, "passed": False, "reason": "File exists but missing required keys."})
                total_score += 5
        except Exception as e:
            details.append({"item": "Deliverable file exists and JSON schema is valid", "score": 0, "max_score": 20, "passed": False, "reason": f"File exists but invalid JSON: {e}"})
    else:
        details.append({"item": "Deliverable file exists and JSON schema is valid", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables/final_report.json not found."})

    # Check 2 & 3
    if agent_data and isinstance(agent_data, dict):
        # Check 2: Total Hours (40 pts)
        agent_hours = agent_data.get("total_valid_hours", None)
        if agent_hours == gold_total_hours:
            details.append({"item": "Accurate total valid hours calculation", "score": 40, "max_score": 40, "passed": True, "reason": f"Correct total_valid_hours: {agent_hours}"})
            total_score += 40
        else:
            details.append({"item": "Accurate total valid hours calculation", "score": 0, "max_score": 40, "passed": False, "reason": f"Expected {gold_total_hours}, got {agent_hours}."})
            
        # Check 3: Flagged Students (40 pts)
        agent_flagged = agent_data.get("flagged_students", [])
        if not isinstance(agent_flagged, list):
            agent_flagged = []
            
        if agent_flagged == gold_flagged:
            details.append({"item": "Accurate flagged students extraction and sorting", "score": 40, "max_score": 40, "passed": True, "reason": "Flagged students list is perfectly matched and sorted."})
            total_score += 40
        elif set(agent_flagged) == set(gold_flagged):
            details.append({"item": "Accurate flagged students extraction and sorting", "score": 30, "max_score": 40, "passed": False, "reason": "Flagged students match but are not properly sorted."})
            total_score += 30
        else:
            missing = len(set(gold_flagged) - set(agent_flagged))
            extra = len(set(agent_flagged) - set(gold_flagged))
            details.append({"item": "Accurate flagged students extraction and sorting", "score": 0, "max_score": 40, "passed": False, "reason": f"List mismatch. Missing: {missing}, Extra: {extra}. Must be exact match."})
    else:
        details.append({"item": "Accurate total valid hours calculation", "score": 0, "max_score": 40, "passed": False, "reason": "No valid JSON data."})
        details.append({"item": "Accurate flagged students extraction and sorting", "score": 0, "max_score": 40, "passed": False, "reason": "No valid JSON data."})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace_dir)
