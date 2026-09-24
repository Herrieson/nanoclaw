import os
import sys
import json
import csv
import httpx
import re
from openai import OpenAI
from dateutil import parser

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
    # Calculate exactly how many valid HR records there should be
    terminals_dir = os.path.join(workspace, "kiosk_data", "terminals")
    valid_terminals = ["T01", "T02", "T03", "T05"] # Hardcoded based on expected env, or parse terminal_status.json
    
    status_file = os.path.join(workspace, "config", "terminal_status.json")
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            status_data = json.load(f)
            valid_terminals = [t for t, v in status_data.items() if v.get("status") == "ACTIVE"]

    keywords = ["health insurance", "medical coverage", "dental plan", "copay dispute", "benefits escalation"]
    keywords_file = os.path.join(workspace, "config", "escalation_keywords.txt")
    if os.path.exists(keywords_file):
        with open(keywords_file, "r") as f:
            lines = f.readlines()
            keywords = [l.strip().lower() for l in lines if l.strip() and not l.startswith("#")]

    valid_hr_records = []
    insurance_records = []

    for t in valid_terminals:
        t_path = os.path.join(terminals_dir, t)
        if not os.path.exists(t_path):
            continue
        for fname in os.listdir(t_path):
            fpath = os.path.join(t_path, fname)
            if fname.endswith(".json"):
                with open(fpath, "r") as f:
                    data = json.load(f)
                    for r in data:
                        if r.get("dept_code") == "HRP-802":
                            dt = parser.parse(r["timestamp"])
                            valid_hr_records.append({"t": dt, "name": r["visitor_name"], "reason": r["inquiry_text"]})
            elif fname.endswith(".txt"):
                with open(fpath, "r") as f:
                    for line in f:
                        # [time] ID:... | CODE:... | USR:... | MSG:...
                        match = re.match(r"\[(.*?)\]\s+ID:.*?\|\s+CODE:(.*?)\s+\|\s+USR:(.*?)\s+\|\s+MSG:(.*)", line)
                        if match:
                            dt_str, code, usr, msg = match.groups()
                            if code.strip() == "HRP-802":
                                dt = parser.parse(dt_str.strip())
                                valid_hr_records.append({"t": dt, "name": usr.strip(), "reason": msg.strip()})

    valid_hr_records.sort(key=lambda x: x["t"])
    
    for r in valid_hr_records:
        reason_lower = r["reason"].lower()
        if any(k in reason_lower for k in keywords):
            insurance_records.append(r)

    return valid_hr_records, insurance_records

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    processed_dir = os.path.join(workspace, "processed")
    csv_file = os.path.join(processed_dir, "daily_appointments.csv")
    txt_file = os.path.join(processed_dir, "insurance_complaints.txt")

    # 1. Directory and Files Existence
    if os.path.exists(processed_dir) and os.path.exists(csv_file) and os.path.exists(txt_file):
        score += 10
        details.append({"item": "Directories and Output Files Created", "score": 10, "max_score": 10, "passed": True, "reason": "processed dir and output files exist."})
    else:
        details.append({"item": "Directories and Output Files Created", "score": 0, "max_score": 10, "passed": False, "reason": "Missing processed dir or output files."})
        return {"total_score": score, "details": details}

    try:
        gt_hr, gt_ins = calculate_ground_truth(workspace)
    except Exception as e:
        details.append({"item": "Ground Truth Calculation Error (Env Issue)", "score": 0, "max_score": 0, "passed": False, "reason": str(e)})
        return {"total_score": score, "details": details}

    # 2. CSV Parsing & Exact Matching
    csv_valid = True
    parsed_hr = []
    has_garbage = False
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers != ["Time", "Name", "Reason"]:
                csv_valid = False
                details.append({"item": "CSV Headers Check", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected ['Time', 'Name', 'Reason'], got {headers}"})
            else:
                score += 10
                details.append({"item": "CSV Headers Check", "score": 10, "max_score": 10, "passed": True, "reason": "Headers are correct."})
            
            for row in reader:
                parsed_hr.append(row)
                if "TEST_DATA_NULL_POINTER_EXCEPTION" in row.get("Reason", ""):
                    has_garbage = True
    except Exception as e:
        csv_valid = False
        details.append({"item": "CSV Read Error", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})

    # 3. CSV Data Integrity & Garbage Filter Check
    if has_garbage:
        details.append({"item": "Terminal Maintenance Data Filter", "score": 0, "max_score": 20, "passed": False, "reason": "Found corrupted data from T04. Agent failed to check config/terminal_status.json."})
    else:
        if len(parsed_hr) == len(gt_hr):
            score += 20
            details.append({"item": "Terminal Maintenance Data Filter & Exact Count", "score": 20, "max_score": 20, "passed": True, "reason": f"Perfect record count match: {len(parsed_hr)} records."})
        else:
            partial_score = 5
            score += partial_score
            details.append({"item": "Terminal Maintenance Data Filter & Exact Count", "score": partial_score, "max_score": 20, "passed": False, "reason": f"Expected {len(gt_hr)} records, found {len(parsed_hr)}. Agent missed some valid records or included invalid ones."})

    # 4. Chronological Sorting & Time Formatting
    time_sorted = True
    format_correct = True
    prev_time = None
    for row in parsed_hr:
        t_str = row.get("Time", "")
        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", t_str):
            format_correct = False
            break
        dt = parser.parse(t_str)
        if prev_time and dt < prev_time:
            time_sorted = False
            break
        prev_time = dt
    
    if format_correct and time_sorted and len(parsed_hr) > 0:
        score += 25
        details.append({"item": "Time Formatted and Chronological Sorting", "score": 25, "max_score": 25, "passed": True, "reason": "Time formats are perfectly unified to YYYY-MM-DD HH:MM:SS and strictly ordered."})
    else:
        details.append({"item": "Time Formatted and Chronological Sorting", "score": 0, "max_score": 25, "passed": False, "reason": "Failed chronological sorting or time format not unified."})

    # 5. TXT format and Keyword Filtering
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            txt_lines = [l.strip() for l in f.readlines() if l.strip()]
        
        if len(txt_lines) == len(gt_ins):
            score += 15
            details.append({"item": "Escalation Keywords Filtering", "score": 15, "max_score": 15, "passed": True, "reason": f"Correctly extracted {len(gt_ins)} insurance complaints."})
        else:
            details.append({"item": "Escalation Keywords Filtering", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {len(gt_ins)} lines, got {len(txt_lines)}."})
            
        # 6. LLM Validation for Semantic Purity
        if len(txt_lines) > 0:
            sample_text = "\n".join(txt_lines[:5])
            prompt = "Check the following list. Does every single item appear to be a complaint or escalation regarding health insurance, medical coverage, dental plan, copay, or benefits? If yes, respond 'YES', otherwise 'NO'."
            is_valid_semantics = llm_judge_content(prompt, sample_text)
            
            if is_valid_semantics:
                score += 20
                details.append({"item": "LLM Semantic Validation", "score": 20, "max_score": 20, "passed": True, "reason": "LLM confirms the extracted list focuses on sensitive insurance complaints."})
            else:
                details.append({"item": "LLM Semantic Validation", "score": 0, "max_score": 20, "passed": False, "reason": "LLM detected non-insurance or irregular records in the complaints file."})
        else:
            details.append({"item": "LLM Semantic Validation", "score": 0, "max_score": 20, "passed": False, "reason": "No data in text file to validate."})
            
    except Exception as e:
        details.append({"item": "TXT Read/Validation Error", "score": 0, "max_score": 35, "passed": False, "reason": str(e)})

    return {"total_score": score, "details": details}

if __name__ == "__main__":
    result = verify()
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(json.dumps(result, indent=4))
