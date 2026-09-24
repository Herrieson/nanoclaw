import os
import sys
import json
import httpx
from openai import OpenAI
import glob
import re

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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. 目录检查
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "Deliverables directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory `deliverables` was created."})
        total_score += 10
    else:
        score_details.append({"item": "Deliverables directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory `deliverables` is missing."})
        # 严重错误，直接返回
        return write_score(total_score, score_details)
        
    files = []
    for root, dirs, filenames in os.walk(deliverables_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                files.append({"name": filename, "content": content})
                
    if len(files) >= 3:
        score_details.append({"item": "Generated at least 3 files", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {len(files)} files in deliverables."})
        total_score += 10
    else:
        score_details.append({"item": "Generated at least 3 files", "score": 0, "max_score": 10, "passed": False, "reason": f"Found only {len(files)} files, expected at least 3 (quarantine, alerts, valid inventory)."})
        
    # Check variables
    found_quarantine = False
    found_alert = False
    found_tally = False
    
    tally_score = 0
    quarantine_score = 0
    alert_score = 0
    
    for file_info in files:
        content = file_info["content"].lower()
        
        # Identity Check 1: Quarantine file (Contains expired: Lisinopril, Adderall. Not unexpired ones)
        if "lisinopril" in content:
            found_quarantine = True
            # Validate quarantine logic
            if "amoxicillin" not in content and "ibuprofen" not in content:
                quarantine_score = 25
            else:
                quarantine_score = 10 # Mixed unexpired items
                
        # Identity Check 2: Schedule II Alert (Contains Oxycodone. No Rx or OTC like Amoxicillin/Ibuprofen)
        # Note: Adderall is also CII, could be here even if expired.
        if "oxycodone" in content and "lisinopril" not in content and file_info["name"] != "logs/weekend_inventory.csv":
            # Using LLM to ensure it's framed as an alert / strict list if needed, or just check content
            if "amoxicillin" not in content and "ibuprofen" not in content:
                alert_score = 15
                if llm_judge_content("Does this file represent an alert, warning, or secure list for Schedule II (CII) medications?", file_info["content"]):
                    alert_score += 10
                    found_alert = True
                
        # Identity Check 3: Valid Inventory Tally
        if "800" in content and "amoxicillin" in content:
            found_tally = True
            if "1000" in content and "ibuprofen" in content:
                if "100" in content and "oxycodone" in content:
                    tally_score = 30
                    if "lisinopril" not in content and "adderall" not in content: # No expired items should be here
                        tally_score += 10
    
    total_score += quarantine_score
    score_details.append({"item": "Quarantine list generated correctly", "score": quarantine_score, "max_score": 25, "passed": quarantine_score == 25, "reason": f"Score {quarantine_score}/25 for expired medication list."})
    
    total_score += alert_score
    score_details.append({"item": "Schedule II Alert list generated correctly", "score": alert_score, "max_score": 25, "passed": alert_score == 25, "reason": f"Score {alert_score}/25 for CII alert list."})

    total_score += tally_score
    score_details.append({"item": "Valid inventory tally calculated correctly", "score": tally_score, "max_score": 40, "passed": tally_score == 40, "reason": f"Score {tally_score}/40 for final clean inventory numbers."})

    write_score(total_score, score_details)

def write_score(total_score, details):
    report = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    verify()
