import os
import sys
import json
import httpx
import csv
import re
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    finance_dir = os.path.join(workspace, "finance_summary")
    score_details = []
    total_score = 0

    # 1. Check directory and file existence (10 points)
    dir_exists = os.path.isdir(finance_dir)
    files = os.listdir(finance_dir) if dir_exists else []
    report_file = None
    if dir_exists and files:
        report_file = os.path.join(finance_dir, files[0])
        score_details.append({"item": "Directory and file creation", "score": 10, "max_score": 10, "passed": True, "reason": "Found file in finance_summary"})
        total_score += 10
    else:
        score_details.append({"item": "Directory and file creation", "score": 0, "max_score": 10, "passed": False, "reason": "No summary file found in finance_summary/"})
        # If no file, we output and exit early
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # Read content for further checks
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        score_details.append({"item": "File readability", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 2. Financial Accuracy: Net Cash (40 points)
    # Expected: (85+30+55) - (45.50+22+15+12) = 170 - 94.50 = 75.50
    # Search for the number 75.5 or 75.50 using regex
    found_cash = re.search(r'75\.5', content)
    if found_cash:
        score_details.append({"item": "Net Cash Calculation", "score": 40, "max_score": 40, "passed": True, "reason": "Correct net cash ($75.50) identified."})
        total_score += 40
    else:
        score_details.append({"item": "Net Cash Calculation", "score": 0, "max_score": 40, "passed": False, "reason": "Did not find correct net cash amount ($75.50)."})

    # 3. Debtor Accuracy: Sinvergüenzas list (30 points)
    # Expected: Elena ($120), Mrs. Smith ($90), Sofia ($40)
    debtors = ["Elena", "Smith", "Sofia"]
    found_debtors = [d for d in debtors if d.lower() in content.lower()]
    debtor_score = (len(found_debtors) / len(debtors)) * 30
    score_details.append({
        "item": "Debtor Identification", 
        "score": int(debtor_score), 
        "max_score": 30, 
        "passed": len(found_debtors) == 3, 
        "reason": f"Found {len(found_debtors)}/3 debtors: {', '.join(found_debtors)}"
    })
    total_score += int(debtor_score)

    # 4. LLM Judge: Persona and Tone (20 points)
    # Check if it's "clean and easy to read" and respects the "stressed hairdresser" context
    prompt = "Does this summary provide a clear, empathetic overview suitable for a stressed business owner, and explicitly list people who owe money?"
    is_good_tone = llm_judge_content(prompt, content)
    if is_good_tone:
        score_details.append({"item": "Tone and Clarity (LLM Judge)", "score": 20, "max_score": 20, "passed": True, "reason": "Report is professional and meets persona needs."})
        total_score += 20
    else:
        score_details.append({"item": "Tone and Clarity (LLM Judge)", "score": 0, "max_score": 20, "passed": False, "reason": "Report format or tone is poor."})

    # Final score output
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    verify()
