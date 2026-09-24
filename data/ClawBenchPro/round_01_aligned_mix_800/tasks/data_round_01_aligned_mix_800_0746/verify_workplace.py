import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

# -----------------------------------------------------------------------------
# Configuration & LLM Setup
# -----------------------------------------------------------------------------
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
        content = response.choices[0].message.content.strip().lower()
        return "yes" in content
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# -----------------------------------------------------------------------------
# Validation Logic
# -----------------------------------------------------------------------------
def run_evaluation(workspace):
    score_details = []
    report_dir = os.path.join(workspace, "audit_reports")
    
    # 1. Directory Structure (10 points)
    dir_exists = os.path.exists(report_dir) and os.path.isdir(report_dir)
    score_details.append({
        "item": "Check audit_reports directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory audit_reports found" if dir_exists else "Directory audit_reports missing"
    })

    # Find the report file (allow common names like summary.json, audit.json, etc.)
    report_file = None
    if dir_exists:
        files = os.listdir(report_dir)
        if files:
            report_file = os.path.join(report_dir, files[0])

    if not report_file or not os.path.exists(report_file):
        score_details.append({"item": "Audit report file content", "score": 0, "max_score": 90, "passed": False, "reason": "No report file generated."})
        return score_details

    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 2. Ghost Stock Calculation (40 points)
        # Expected: 
        # PUMP-001: Ship 10, Sold 10 (OK)
        # GEN-500: Ship 2, Sold 2 (OK)
        # VALVE-22: Ship 50 (after deduplication/cleaning), Sold 100 -> Ghost 50
        # DRILL-X: Ship 5, Sold 15 -> Ghost 10
        # TRACTOR-09: Ship 0, Sold 1 -> Ghost 1
        ghost_score = 0
        if "DRILL-X" in content and "10" in content: ghost_score += 15
        if "VALVE-22" in content and "50" in content: ghost_score += 15
        if "TRACTOR-09" in content and "1" in content: ghost_score += 10
        
        score_details.append({
            "item": "Ghost Stock accuracy (DRILL-X: 10, VALVE-22: 50, TRACTOR-09: 1)",
            "score": ghost_score,
            "max_score": 40,
            "passed": ghost_score == 40,
            "reason": f"Calculated score based on item matches in report: {ghost_score}/40"
        })

        # 3. Revenue Loss Calculation (30 points)
        # Returns: 2 units GEN-500 ($4500 ea) + 1 unit VALVE-22 ($45 ea)
        # Total = 9000 + 45 = 9045
        has_correct_loss = "9045" in content.replace(",", "").replace("$", "")
        score_details.append({
            "item": "Total projected revenue loss calculation ($9045)",
            "score": 30 if has_correct_loss else 0,
            "max_score": 30,
            "passed": has_correct_loss,
            "reason": "Correct loss value 9045 found" if has_correct_loss else "Incorrect loss value"
        })

        # 4. LLM Analysis: Professionalism & Data Cleaning Logic (20 points)
        prompt = (
            "Determine if the audit report effectively summarizes the inventory discrepancies. "
            "The supervisor asked to filter out 'typos' like negative quantities (PUMP-001 has a -5 record). "
            "Does the report present the information clearly and mention cleaning/filtering or present clean data? "
            "Answer YES only if it looks like a professional audit report."
        )
        llm_pass = llm_judge_content(prompt, content)
        score_details.append({
            "item": "Professionalism and data cleaning validation via LLM",
            "score": 20 if llm_pass else 0,
            "max_score": 20,
            "passed": llm_pass,
            "reason": "LLM confirmed report is professional and accounts for data cleaning" if llm_pass else "LLM rejected report quality"
        })

    except Exception as e:
        score_details.append({"item": "File Parsing Error", "score": 0, "max_score": 90, "passed": False, "reason": str(e)})

    return score_details

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    details = run_evaluation(workspace_path)
    total_score = sum(d["score"] for d in details)
    
    output = {
        "total_score": min(100, total_score),
        "details": details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=4)
