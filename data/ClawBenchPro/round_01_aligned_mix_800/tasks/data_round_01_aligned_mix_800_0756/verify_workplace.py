import os
import sys
import json
import httpx
import re
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
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def calculate_expected_data():
    # Calculation based on env_builder:
    # W1: Mon (09:00-15:00 = 6h), Thu (14:00-18:00 = 4h) -> 10h
    # W2: Tue (10:00-16:00 = 6h), Fri (08:00-14:00 = 6h) -> 12h
    # W3: Thu (16:00-20:00 = 4h) -> 4h
    # Total Hours: 10 + 12 + 4 = 26 hours
    # Pay: 26 * 14.50 = 377.00
    # Conflicts (Thu 15:00-17:00):
    # 2023-10-12: 14:00-18:00 (CONFLiCT)
    # 2023-10-26: 16:00-20:00 (CONFLICT)
    return 377.00, ["2023-10-12", "2023-10-26"]

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    fp_dir = os.path.join(workspace, "family_planning")
    score = 0
    details = []

    # 1. Check Directory and File Existence (10 points)
    files_in_fp = os.listdir(fp_dir) if os.path.exists(fp_dir) else []
    report_file = None
    if files_in_fp:
        report_file = os.path.join(fp_dir, files_in_fp[0])
        score += 10
        details.append({"item": "Directory existence", "score": 10, "max_score": 10, "passed": True, "reason": f"Found report: {files_in_fp[0]}"})
    else:
        details.append({"item": "Directory existence", "score": 0, "max_score": 10, "passed": False, "reason": "No report found in family_planning"})

    if report_file:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. Check Paycheck Calculation (40 points)
        # Expected: 377.00. Using regex to find the number in the text.
        expected_pay = 377.00
        # Look for 377 or 377.00
        pay_match = re.search(r"377(\.00)?", content)
        if pay_match:
            score += 40
            details.append({"item": "Paycheck calculation", "score": 40, "max_score": 40, "passed": True, "reason": "Calculated $377.00 correctly"})
        else:
            details.append({"item": "Paycheck calculation", "score": 0, "max_score": 40, "passed": False, "reason": "Could not find $377.00 in the report"})

        # 3. Check Conflict Dates (30 points)
        # Expected: 2023-10-12 and 2023-10-26
        has_oct_12 = "2023-10-12" in content or "October 12" in content
        has_oct_26 = "2023-10-26" in content or "October 26" in content
        
        if has_oct_12 and has_oct_26:
            score += 30
            details.append({"item": "Conflict identification", "score": 30, "max_score": 30, "passed": True, "reason": "Both conflict dates identified"})
        elif has_oct_12 or has_oct_26:
            score += 15
            details.append({"item": "Conflict identification", "score": 15, "max_score": 30, "passed": False, "reason": "Only one conflict date identified"})
        else:
            details.append({"item": "Conflict identification", "score": 0, "max_score": 30, "passed": False, "reason": "No correct conflict dates found"})

        # 4. LLM Judge: Quality and Persona Matching (20 points)
        # Check if the report is clear and helpful for the user persona
        prompt = "Does this document clearly summarize the total paycheck and the specific dates of schedule conflicts for the user? Is it presented in a way that is easy for a busy person to read?"
        is_clear = llm_judge_content(prompt, content)
        if is_clear:
            score += 20
            details.append({"item": "Report quality (LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "LLM judged the report as clear and helpful"})
        else:
            details.append({"item": "Report quality (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "LLM judged the report as unclear or missing key summaries"})
    else:
        details.append({"item": "Report Content", "score": 0, "max_score": 90, "passed": False, "reason": "No file to evaluate content"})

    # Save results
    result = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
