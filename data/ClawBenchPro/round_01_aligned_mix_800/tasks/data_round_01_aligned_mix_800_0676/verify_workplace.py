import os
import sys
import json
import glob
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "ready_for_review")
    
    # 1. Check directory and file existence (10 points)
    if os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        if files:
            score_details.append({"item": "Check target directory and file existence", "score": 10, "max_score": 10, "passed": True, "reason": "Directory ready_for_review exists and is not empty."})
            total_score += 10
            
            # Read the generated report content
            report_content = ""
            for f in files:
                filepath = os.path.join(target_dir, f)
                if os.path.isfile(filepath):
                    with open(filepath, 'r', encoding='utf-8') as file:
                        report_content += file.read() + "\n"
        else:
            score_details.append({"item": "Check target directory and file existence", "score": 0, "max_score": 10, "passed": False, "reason": "Directory exists but is empty."})
            report_content = ""
    else:
        score_details.append({"item": "Check target directory and file existence", "score": 0, "max_score": 10, "passed": False, "reason": "Directory ready_for_review does not exist."})
        report_content = ""

    if report_content:
        # 2. Check Deductible Total (25 points)
        prompt_deductible = "Does the report explicitly state that the total deductible expense is EXACTLY 1551.00 or 1551? Evaluate strictly. If it's incorrect or missing, answer NO."
        if llm_judge_content(prompt_deductible, report_content):
            score_details.append({"item": "Accurate deductible calculation", "score": 25, "max_score": 25, "passed": True, "reason": "LLM verified correct deductible total (1551.00)."})
            total_score += 25
        else:
            score_details.append({"item": "Accurate deductible calculation", "score": 0, "max_score": 25, "passed": False, "reason": "Deductible total is incorrect or missing."})

        # 3. Check Non-Deductible Total (25 points)
        prompt_nondeductible = "Does the report explicitly state that the total non-deductible expense is EXACTLY 939.99? Evaluate strictly. If it's incorrect or missing, answer NO."
        if llm_judge_content(prompt_nondeductible, report_content):
            score_details.append({"item": "Accurate non-deductible calculation", "score": 25, "max_score": 25, "passed": True, "reason": "LLM verified correct non-deductible total (939.99)."})
            total_score += 25
        else:
            score_details.append({"item": "Accurate non-deductible calculation", "score": 0, "max_score": 25, "passed": False, "reason": "Non-deductible total is incorrect or missing."})

        # 4. Check Flagged Employee (20 points)
        prompt_flagged = "Does the report explicitly flag the employee 'EMP-042' for having more than two non-deductible items? Answer NO if 'EMP-042' is not flagged or if other employees are wrongly flagged."
        if llm_judge_content(prompt_flagged, report_content):
            score_details.append({"item": "Accurate employee flagging", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified EMP-042 was flagged correctly."})
            total_score += 20
        else:
            score_details.append({"item": "Accurate employee flagging", "score": 0, "max_score": 20, "passed": False, "reason": "EMP-042 was not flagged correctly or there are hallucinations."})

        # 5. Check Professionalism & Tone (20 points)
        prompt_tone = "Is the report presented in a clean, professional manner without excessive conversational filler, suitable for a strict Senior Accounting Manager?"
        if llm_judge_content(prompt_tone, report_content):
            score_details.append({"item": "Professional tone and format", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified professional tone."})
            total_score += 20
        else:
            score_details.append({"item": "Professional tone and format", "score": 0, "max_score": 20, "passed": False, "reason": "Tone was deemed unprofessional or messy."})

    else:
        score_details.append({"item": "Accurate deductible calculation", "score": 0, "max_score": 25, "passed": False, "reason": "No report to check."})
        score_details.append({"item": "Accurate non-deductible calculation", "score": 0, "max_score": 25, "passed": False, "reason": "No report to check."})
        score_details.append({"item": "Accurate employee flagging", "score": 0, "max_score": 20, "passed": False, "reason": "No report to check."})
        score_details.append({"item": "Professional tone and format", "score": 0, "max_score": 20, "passed": False, "reason": "No report to check."})

    # Output score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
