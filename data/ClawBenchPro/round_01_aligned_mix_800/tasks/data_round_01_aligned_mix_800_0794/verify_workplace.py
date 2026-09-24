import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# Configuration for LLM
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
        res = response.choices[0].message.content.strip().lower()
        return "yes" in res
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    
    target_dir = os.path.join(workspace, "for_mateo")
    
    # 1. Structure Check (10 points)
    dir_exists = os.path.exists(target_dir)
    score_details.append({
        "item": "Directory 'for_mateo' exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found directory" if dir_exists else "Directory missing"
    })

    if not dir_exists:
        # Cannot continue deep check if directory is missing
        final_score = sum(d['score'] for d in score_details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f)
        return

    # Find the summary file (allow any extension but check content)
    files = os.listdir(target_dir)
    target_file = None
    for f in files:
        if "vip" in f.lower() or "summary" in f.lower() or "mateo" in f.lower() or len(files) == 1:
            target_file = os.path.join(target_dir, f)
            break

    if not target_file:
        score_details.append({"item": "Summary file exists", "score": 0, "max_score": 40, "passed": False, "reason": "No summary file found in for_mateo"})
    else:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. Calculation Verification (40 points)
        # Total Tips: 800+450+1200+600+0+100+750 = 3900
        # Expenses: 1200 + 850 + 450 = 2500
        # Net Profit: 3900 - 2500 = 1400
        correct_profit = "1400"
        has_profit = correct_profit in content
        score_details.append({
            "item": "Correct Net Profit Calculation ($1400)",
            "score": 40 if has_profit else 0,
            "max_score": 40,
            "passed": has_profit,
            "reason": "Found $1400 in file" if has_profit else "Correct profit amount $1400 not found"
        })

        # 3. Data Cleaning - VIP Filter (30 points)
        # VIPs: Mr. Anderson, Isabella Torres, Julian Vance, Sophia Sterling, Marcus Reed
        # Tipped > 500: Mr. Anderson(800), Julian Vance(1200), Sophia Sterling(600)
        # Lucia Gomez is NOT a VIP. Crash Override is NOT a VIP.
        vips_correct = ("Mr. Anderson" in content and "Julian Vance" in content and "Sophia Sterling" in content)
        no_crashers = ("Lucia Gomez" not in content and "Crash Override" not in content)
        
        passed_filter = vips_correct and no_crashers
        score_details.append({
            "item": "VIP Filtering (Tips > $500 and on VIP list)",
            "score": 30 if passed_filter else (15 if vips_correct else 0),
            "max_score": 30,
            "passed": passed_filter,
            "reason": "Correctly filtered VIPs" if passed_filter else "Missing VIPs or included crashers"
        })

        # 4. LLM Tone & Requirement Check (20 points)
        # Checking if it's a "clean list" and follows the persona request
        prompt = "Check if the file provides a clear list of names and explicitly mentions the net profit for Mateo's records as requested. The tone should be helpful."
        llm_passed = llm_judge_content(prompt, content)
        score_details.append({
            "item": "LLM Semantic Check: Format and Profit Mention",
            "score": 20 if llm_passed else 0,
            "max_score": 20,
            "passed": llm_passed,
            "reason": "LLM verified content structure and profit mention" if llm_passed else "LLM failed content verification"
        })

    total_score = sum(d['score'] for d in score_details)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    verify()
