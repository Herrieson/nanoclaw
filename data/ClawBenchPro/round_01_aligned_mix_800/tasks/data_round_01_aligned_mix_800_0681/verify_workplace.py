import os
import sys
import json
import httpx
import re
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
    reports_dir = os.path.join(workspace, "reports")
    
    score_details = []
    total_score = 0
    
    # 1. Structure Check: Directory exists (10)
    if os.path.isdir(reports_dir):
        score_details.append({"item": "Check if 'reports' directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'reports' exists."})
        total_score += 10
    else:
        score_details.append({"item": "Check if 'reports' directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'reports' not found."})
        
    # 2. Structure Check: Files exist (10)
    report_files = []
    if os.path.isdir(reports_dir):
        for f in os.listdir(reports_dir):
            file_path = os.path.join(reports_dir, f)
            if os.path.isfile(file_path):
                report_files.append(file_path)
    
    if report_files:
        score_details.append({"item": "Check if report files are created", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {len(report_files)} file(s) in 'reports'."})
        total_score += 10
    else:
        score_details.append({"item": "Check if report files are created", "score": 0, "max_score": 10, "passed": False, "reason": "No files found in 'reports' directory."})
        
    # Aggregate content for scanning
    all_content = ""
    for f in report_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                all_content += f"\n--- File: {os.path.basename(f)} ---\n"
                all_content += file.read()
        except Exception as e:
            pass

    # 3. Deterministic Data Parsing: Total Overcharge Amount (30)
    # The total overcharge is exactly 14.00. We look for '14' or '14.00' as standalone words/numbers.
    if not all_content.strip():
        score_details.append({"item": "Accurate total overcharge calculation", "score": 0, "max_score": 30, "passed": False, "reason": "No file content to parse."})
    else:
        # Regex to match 14 or 14.00 securely, preventing matches inside larger numbers like 140 or 3.14
        if re.search(r'\b14(?:\.00)?\b', all_content):
            score_details.append({"item": "Accurate total overcharge calculation", "score": 30, "max_score": 30, "passed": True, "reason": "Successfully extracted exact overcharge amount: 14.00."})
            total_score += 30
        else:
            score_details.append({"item": "Accurate total overcharge calculation", "score": 0, "max_score": 30, "passed": False, "reason": "Did not find the exact calculated amount of 14.00 in the reports."})
            
    # 4. Deterministic Data Parsing: Low Stock Items (20)
    # True targets (total < 5): WAX_002, SOAP_005, BRUSH_004
    # Safe negative target: MOP_003 (qty=5, exactly threshold but instruction says LESS THAN 5)
    low_stock_targets = [("WAX_002", "High-Gloss Floor Wax"), ("SOAP_005", "Antibacterial Hand Soap"), ("BRUSH_004", "Scrub Brush")]
    
    if all_content.strip():
        found_targets = 0
        for id_str, name_str in low_stock_targets:
            if id_str.lower() in all_content.lower() or name_str.lower() in all_content.lower():
                found_targets += 1
                
        base_score = 0
        if found_targets == 3:
            base_score = 20
        else:
            base_score = found_targets * 6  # Sub-gradient

        # Penalty check for MOP_003 (which is exactly 5 and should NOT be in the low stock list)
        penalty = 0
        if "mop_003" in all_content.lower() or "microfiber mop head" in all_content.lower():
            penalty = 5
            
        final_stock_score = max(0, base_score - penalty)
        passed = (final_stock_score == 20)
        
        reason = f"Found {found_targets}/3 target items."
        if penalty > 0:
            reason += " Penalized for mistakenly including non-low-stock item MOP_003."
        if passed:
            reason = "Perfectly identified all low stock items without false positives."
            
        score_details.append({"item": "Low stock items identification", "score": final_stock_score, "max_score": 20, "passed": passed, "reason": reason})
        total_score += final_stock_score
    else:
        score_details.append({"item": "Low stock items identification", "score": 0, "max_score": 20, "passed": False, "reason": "No content to check."})

    # 5. LLM Validation: Formal Format & Separation (20)
    if all_content.strip():
        # Sub-check A: Formal Tone (10)
        prompt_formal = "Evaluate the content provided. Does it contain a formal 'Discrepancy Report' with professional formatting (e.g., proper title, clear context, business-like tone) rather than just an unformatted raw data dump?"
        if llm_judge_content(prompt_formal, all_content):
            score_details.append({"item": "Formal report formatting", "score": 10, "max_score": 10, "passed": True, "reason": "The report exhibits a formal and professional tone."})
            total_score += 10
        else:
            score_details.append({"item": "Formal report formatting", "score": 0, "max_score": 10, "passed": False, "reason": "The content lacks formal report formatting."})
            
        # Sub-check B: Clear Separation (10)
        prompt_separate = "Does the content clearly separate the 'Low Stock' list from the 'Discrepancy Report' (e.g., they are in different distinct files, or have unmistakable and completely separate section headers)?"
        if llm_judge_content(prompt_separate, all_content):
            score_details.append({"item": "Separation of concerns", "score": 10, "max_score": 10, "passed": True, "reason": "The Low Stock list is clearly separated."})
            total_score += 10
        else:
            score_details.append({"item": "Separation of concerns", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to visually/structurally separate the Discrepancy Report from the Low Stock list."})
    else:
        score_details.append({"item": "Formal report formatting", "score": 0, "max_score": 10, "passed": False, "reason": "No content."})
        score_details.append({"item": "Separation of concerns", "score": 0, "max_score": 10, "passed": False, "reason": "No content."})

    # Output results
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
