import os
import sys
import json
import csv
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
        result = response.choices[0].message.content.strip().lower()
        return "yes" in result
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    report_file = os.path.join(deliverables_path, "report.json")
    memo_file = os.path.join(deliverables_path, "memo.md")
    
    score_details = []
    
    # 1. Structure Check (10 points)
    dir_exists = os.path.exists(deliverables_path)
    score_details.append({
        "item": "Directory 'deliverables' exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Found deliverables directory" if dir_exists else "Missing deliverables directory"
    })
    
    files_exist = os.path.exists(report_file) and os.path.exists(memo_file)
    score_details.append({
        "item": "Files report.json and memo.md exist",
        "score": 5 if files_exist else 0,
        "max_score": 5,
        "passed": files_exist,
        "reason": "Both files found" if files_exist else "One or more files missing"
    })

    # 2. JSON Content Precision (40 points)
    # Expected violators: Barnes (37.5%), Davis (33.3%)
    # Adams (12.5%), Chen (6.25%) are compliant.
    json_score = 0
    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract names - handle potential variations in naming key
            content_str = str(data).lower()
            found_barnes = "barnes" in content_str
            found_davis = "davis" in content_str
            found_adams = "adams" in content_str
            found_chen = "chen" in content_str
            
            if found_barnes and found_davis and not found_adams and not found_chen:
                json_score = 40
                reason = "Correct violators identified (Barnes, Davis) and no false positives."
            elif found_barnes and found_davis:
                json_score = 20
                reason = "Correct violators found but includes false positives (Adams or Chen)."
            elif found_barnes or found_davis:
                json_score = 10
                reason = "Only partial violators identified."
            else:
                json_score = 0
                reason = "No correct violators identified."
        except Exception as e:
            reason = f"JSON parse error: {e}"
    else:
        reason = "Report file missing."
    
    score_details.append({
        "item": "JSON report accuracy (Violator identification)",
        "score": json_score,
        "max_score": 40,
        "passed": json_score == 40,
        "reason": reason
    })

    # 3. Memo Quality & Tone - LLM Judge (50 points)
    memo_score = 0
    if os.path.exists(memo_file):
        with open(memo_file, 'r', encoding='utf-8') as f:
            memo_content = f.read()
        
        # Check tone (Professional but firm, no sugarcoating)
        tone_ok = llm_judge_content(
            "Does this memo sound professional but firm and direct, avoiding 'sugarcoating' or overly soft language? It should be addressed to a department head about inefficiencies.", 
            memo_content
        )
        # Check if it mentions the policy violation (20% cap)
        policy_ok = llm_judge_content(
            "Does this memo explicitly mention the administrative time cap (20%) or the specific inefficiencies/violations found in the data?",
            memo_content
        )
        
        if tone_ok: memo_score += 25
        if policy_ok: memo_score += 25
        
        score_details.append({
            "item": "Memo Tone (Firm/Professional)",
            "score": 25 if tone_ok else 0,
            "max_score": 25,
            "passed": tone_ok,
            "reason": "Tone matches persona requirements" if tone_ok else "Tone is too soft or unprofessional"
        })
        score_details.append({
            "item": "Memo Substance (Policy/Findings)",
            "score": 25 if policy_ok else 0,
            "max_score": 25,
            "passed": policy_ok,
            "reason": "Correctly references the 20% cap or specific data findings" if policy_ok else "Lacks specific policy context or findings"
        })
    else:
        score_details.append({
            "item": "Memo Content Validation",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "Memo file missing"
        })

    total_score = sum(d['score'] for d in score_details)
    
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
