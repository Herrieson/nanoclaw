import os
import sys
import json
import csv
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    audit_report_dir = os.path.join(workspace, "audit_report")
    clean_csv = os.path.join(audit_report_dir, "clean_attendance.csv")
    unauth_txt = os.path.join(audit_report_dir, "unauthorized.txt")

    # 1. Check Directory
    if os.path.isdir(audit_report_dir):
        details.append({"item": "Check if audit_report directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
        total_score += 10
    else:
        details.append({"item": "Check if audit_report directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory does not exist."})
        
    # 2. Check Clean Attendance CSV
    if os.path.isfile(clean_csv):
        details.append({"item": "Check if clean_attendance.csv exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
        total_score += 10
        
        # Parse CSV strictly
        try:
            with open(clean_csv, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            csv_text = " ".join([" ".join(row).lower() for row in rows])
            
            # Valid attendees that must be present
            valid_attendees = [
                ("alice smith", "hr-core"),
                ("robert chen", "it-support"),
                ("maria", "exec-admin"), # allow Maria G. or Maria Garcia
                ("linda taylor", "hr-core")
            ]
            
            score_per_attendee = 10
            csv_score = 0
            missing_attendees = []
            
            for name, dept in valid_attendees:
                if name in csv_text and dept in csv_text:
                    csv_score += score_per_attendee
                else:
                    missing_attendees.append(name)
            
            # Check for unauthorized or absent people (strict deduction)
            unauthorized = ["greggory", "house", "chad", "bro", "james wilson"]
            has_unauth = any(u in csv_text for u in unauthorized)
            
            if has_unauth:
                details.append({"item": "Clean attendance CSV content check", "score": 0, "max_score": 40, "passed": False, "reason": "CSV contains unauthorized or absent individuals! Strict penalty applied."})
            else:
                details.append({"item": "Clean attendance CSV content check", "score": csv_score, "max_score": 40, "passed": len(missing_attendees)==0, "reason": f"CSV validated. Missing: {missing_attendees}" if missing_attendees else "All valid attendees correctly recorded."})
                total_score += csv_score
                
        except Exception as e:
            details.append({"item": "Clean attendance CSV content check", "score": 0, "max_score": 40, "passed": False, "reason": f"Failed to parse CSV strictly: {e}"})
    else:
        details.append({"item": "Check if clean_attendance.csv exists", "score": 0, "max_score": 10, "passed": False, "reason": "File does not exist."})
        details.append({"item": "Clean attendance CSV content check", "score": 0, "max_score": 40, "passed": False, "reason": "File missing."})

    # 3. Check Unauthorized TXT
    if os.path.isfile(unauth_txt):
        details.append({"item": "Check if unauthorized.txt exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
        total_score += 10
        
        try:
            with open(unauth_txt, "r", encoding="utf-8") as f:
                unauth_content = f.read()
                
            prompt = (
                "Review the provided text file content. "
                "Does it clearly and accurately list exactly TWO unauthorized people: 'Greggory House' (with ID PA-999) "
                "and 'Chad Bro' (with ID PA-888)? It MUST NOT include authorized employees (like Alice, Robert, Maria, Linda, James). "
                "If it meets these exact criteria, answer YES. Otherwise, answer NO."
            )
            
            is_valid_unauth = llm_judge_content(prompt, unauth_content)
            
            if is_valid_unauth:
                details.append({"item": "Unauthorized TXT semantic check", "score": 30, "max_score": 30, "passed": True, "reason": "LLM verified correct unauthorized attendees."})
                total_score += 30
            else:
                details.append({"item": "Unauthorized TXT semantic check", "score": 0, "max_score": 30, "passed": False, "reason": "LLM rejected the unauthorized list contents."})
        except Exception as e:
             details.append({"item": "Unauthorized TXT semantic check", "score": 0, "max_score": 30, "passed": False, "reason": f"Failed to read file: {e}"})
    else:
        details.append({"item": "Check if unauthorized.txt exists", "score": 0, "max_score": 10, "passed": False, "reason": "File does not exist."})
        details.append({"item": "Unauthorized TXT semantic check", "score": 0, "max_score": 30, "passed": False, "reason": "File missing."})

    # Output Score
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
