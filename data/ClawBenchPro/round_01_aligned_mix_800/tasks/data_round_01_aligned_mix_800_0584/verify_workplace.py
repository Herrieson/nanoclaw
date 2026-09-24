import os
import sys
import json
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
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'. Evaluate carefully whether the text strictly contains the requested information without hallucinated extras."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def calculate_ground_truth(workspace):
    registry_file = os.path.join(workspace, "sys_data", "registry.json")
    approved_ids = set()
    id_to_name = {}
    
    if os.path.exists(registry_file):
        with open(registry_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for user in data.get("users", []):
                id_to_name[user["id"]] = user["name"]
                if user.get("clearance") == "passed":
                    approved_ids.add(user["id"])
                    
    total_minutes = 0
    unapproved_set = set()
    
    logs_dir = os.path.join(workspace, "device_logs")
    if os.path.exists(logs_dir):
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".txt"):  # Strict filter, ignores .bak
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        for line in f:
                            if "[CHECK-IN]" in line:
                                parts = line.strip().split()
                                user_id = None
                                dur = 0
                                for p in parts:
                                    if p.startswith("ID:"):
                                        user_id = p[3:]
                                    elif p.startswith("DUR:"):
                                        dur_str = p[4:].replace("m", "")
                                        try:
                                            dur = int(dur_str)
                                        except:
                                            pass
                                if user_id:
                                    if user_id in approved_ids:
                                        total_minutes += dur
                                    else:
                                        if user_id in id_to_name:
                                            unapproved_set.add(id_to_name[user_id])
                                        else:
                                            unapproved_set.add(user_id)
                                            
    total_hours = total_minutes / 60.0
    
    inbox_dir = os.path.join(workspace, "inbox_scrapes")
    urgent_requests = []
    if os.path.exists(inbox_dir):
        for root, dirs, files in os.walk(inbox_dir):
            for file in files:
                if file.endswith(".json"):
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("priority") == "URGENT" and data.get("demographic") in ["infant", "toddler"]:
                                urgent_requests.append(data.get("request_text", ""))
                    except:
                        pass # Ignore corrupted JSONs safely
                        
    return round(total_hours, 2), sorted(list(unapproved_set)), urgent_requests

def verify_workspace(workspace):
    score_details = []
    total_score = 0
    
    # Check 1: Deliverables Folder and File Existence (10 points)
    deliv_dir = os.path.join(workspace, "deliverables")
    report_content = ""
    has_report = False
    
    if os.path.exists(deliv_dir) and os.path.isdir(deliv_dir):
        files = os.listdir(deliv_dir)
        if len(files) > 0:
            has_report = True
            for f in files:
                file_path = os.path.join(deliv_dir, f)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        report_content += fh.read() + "\n"
    
    if has_report and len(report_content.strip()) > 0:
        score_details.append({"item": "Deliverables Report Exists", "score": 10, "max_score": 10, "passed": True, "reason": "Report file found and read."})
        total_score += 10
    else:
        score_details.append({"item": "Deliverables Report Exists", "score": 0, "max_score": 10, "passed": False, "reason": "No valid report found in deliverables directory."})
        # Fast exit if no report
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Calculate Ground Truth
    gt_hours, gt_unapproved, gt_urgent = calculate_ground_truth(workspace)
    
    # Check 2: Total Valid Volunteer Hours Calculation (30 points)
    # Convert GT hours nicely (e.g. 150.5 to string)
    prompt_hours = f"Does the following report explicitly state that the total valid volunteer hours is {gt_hours} or {int(gt_hours)} (if mathematically equivalent)? Evaluate carefully."
    if llm_judge_content(prompt_hours, report_content):
        score_details.append({"item": "Correct Total Valid Hours", "score": 30, "max_score": 30, "passed": True, "reason": f"Agent correctly reported {gt_hours} hours."})
        total_score += 30
    else:
        score_details.append({"item": "Correct Total Valid Hours", "score": 0, "max_score": 30, "passed": False, "reason": f"Failed to report the exact total hours ({gt_hours}). Likely processed .bak files or failed math."})

    # Check 3: Unapproved Intruders List (30 points)
    prompt_unapproved = f"Does the following report explicitly list ALL of the following unapproved intruders (and NO ONE ELSE as an unapproved intruder)?\nList: {gt_unapproved}"
    if llm_judge_content(prompt_unapproved, report_content):
        score_details.append({"item": "Correct Unapproved Intruders", "score": 30, "max_score": 30, "passed": True, "reason": "Agent correctly cross-referenced registry and identified all intruders without false positives."})
        total_score += 30
    else:
        score_details.append({"item": "Correct Unapproved Intruders", "score": 0, "max_score": 30, "passed": False, "reason": "Failed to list the correct unapproved intruders. May have failed dictionary join or failed to check clearance."})

    # Check 4: Urgent Requests Extraction (30 points)
    prompt_urgent = f"Does the following report explicitly include ALL of the following urgent request texts?\nRequests: {gt_urgent}"
    if llm_judge_content(prompt_urgent, report_content):
        score_details.append({"item": "Correct Urgent Requests", "score": 30, "max_score": 30, "passed": True, "reason": "Agent safely parsed JSONs, handled corruption, and filtered the correct demographics and priorities."})
        total_score += 30
    else:
        score_details.append({"item": "Correct Urgent Requests", "score": 0, "max_score": 30, "passed": False, "reason": "Failed to extract the exact urgent infant/toddler requests. Likely broke on JSON parsing or filtered wrong."})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(work_dir)
