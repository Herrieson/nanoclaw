import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client, strictly disable SSL verification as requested
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """Unified interface for checking unstructured text using LLM."""
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
    
    report_dir = os.path.join(workspace, "final_report")
    report_file = os.path.join(report_dir, "balance_final.txt")
    
    score_details = []
    total_score = 0
    
    # 1. Directory Structure (10 points)
    if os.path.isdir(report_dir):
        score_details.append({"item": "Check if directory 'final_report' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists."})
        total_score += 10
    else:
        score_details.append({"item": "Check if directory 'final_report' exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'final_report' is missing."})

    # 2. File Existence (10 points)
    if os.path.isfile(report_file):
        score_details.append({"item": "Check if file 'balance_final.txt' exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists."})
        total_score += 10
        
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 3. Deterministic Extraction: Total Cleared Donations (20 points)
        # 1500 + 800 + 2200 + 4000 = 8500
        # Tolerates commas (8,500) and decimals (8500.00)
        if re.search(r'8,?500(?:\.00)?\b', content):
            score_details.append({"item": "Extract & Verify Total Cleared Donations (8500)", "score": 20, "max_score": 20, "passed": True, "reason": "Accurate donation calculation found."})
            total_score += 20
        else:
            score_details.append({"item": "Extract & Verify Total Cleared Donations (8500)", "score": 0, "max_score": 20, "passed": False, "reason": "Number 8500 not found. Agent miscalculated donations or missed the V_OK filter."})

        # 4. Deterministic Extraction: Total Expenses (20 points)
        # 1200 + 450 = 1650 (Excluding unapproved and internal_transfer)
        if re.search(r'1,?650(?:\.00)?\b', content):
            score_details.append({"item": "Extract & Verify Total Expenses (1650)", "score": 20, "max_score": 20, "passed": True, "reason": "Accurate expense calculation found."})
            total_score += 20
        else:
            score_details.append({"item": "Extract & Verify Total Expenses (1650)", "score": 0, "max_score": 20, "passed": False, "reason": "Number 1650 not found. Agent miscalculated expenses (failed to drop unapproved/internal transfers)."})

        # 5. Deterministic Extraction: Final Balance (20 points)
        # 8500 - 1650 = 6850
        if re.search(r'6,?850(?:\.00)?\b', content):
            score_details.append({"item": "Extract & Verify Final Balance (6850)", "score": 20, "max_score": 20, "passed": True, "reason": "Accurate final balance calculation found."})
            total_score += 20
        else:
            score_details.append({"item": "Extract & Verify Final Balance (6850)", "score": 0, "max_score": 20, "passed": False, "reason": "Number 6850 not found. Agent failed the final math."})

        # 6. LLM Semantic Check: Tone, Format, and Absence of Code (20 points)
        # Ensures Agent didn't leak its reasoning scripts or logic in the final output.
        llm_prompt = (
            "Analyze the following report. It must strictly present ONLY the final numbers/summary "
            "(Total Cleared Donations, Total Expenses, and Final Balance) in a clean, direct, and professional tone. "
            "It MUST NOT contain any Python scripts, code snippets, calculation logic, JSON schemas, or internal reasoning steps. "
            "If it contains scripts/logic or mentions decoy data like '2023 Summer Picnic', return NO. Otherwise, return YES."
        )
        if llm_judge_content(llm_prompt, content):
            score_details.append({"item": "LLM Verification: Format and Cleanliness", "score": 20, "max_score": 20, "passed": True, "reason": "Report is clean, professional, and follows the constraint to hide logic/scripts."})
            total_score += 20
        else:
            score_details.append({"item": "LLM Verification: Format and Cleanliness", "score": 0, "max_score": 20, "passed": False, "reason": "Report contains forbidden code, internal logic, or is improperly formatted."})

    else:
        score_details.append({"item": "Check if file 'balance_final.txt' exists", "score": 0, "max_score": 10, "passed": False, "reason": "File is missing."})
        # Cascade failures for dependent items
        for item in ["Extract & Verify Total Cleared Donations", "Extract & Verify Total Expenses", "Extract & Verify Final Balance", "LLM Verification: Format and Cleanliness"]:
            score_details.append({"item": item, "score": 0, "max_score": 20, "passed": False, "reason": "Skipped because the target file does not exist."})

    # Output final score JSON
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
