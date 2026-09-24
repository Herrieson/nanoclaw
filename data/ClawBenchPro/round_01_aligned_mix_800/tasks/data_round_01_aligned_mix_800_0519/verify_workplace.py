import os
import sys
import json
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
                {"role": "system", "content": "You are a strict maintenance report auditor. Answer ONLY with 'YES' or 'NO'."},
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
    report_path = os.path.join(workspace, "management/final_report/summary.txt")
    score_details = []
    total_score = 0

    # Expected Values (Calculated from env_builder.py logic)
    # MAC-9901 (Spindle_Assembly), MAC-4502 (Servo_Motor), MAC-1108 (Ball_Screw)
    # Spindle: 950 (2024-05-20 > 2023-01-01)
    # Servo: 1350 (2024-06-15 > 2023-01-01)
    # Ball_Screw: 620 (2024-07-01 > 2023-12-10)
    # Total: 950 + 1350 + 620 = 2920
    expected_ids = ["MAC-9901", "MAC-4502", "MAC-1108"]
    expected_total = 2920

    # 1. Check Directory and File Existence (10 points)
    if os.path.exists(report_path):
        score_details.append({"item": "Report file existence", "score": 10, "max_score": 10, "passed": True, "reason": "summary.txt found."})
        total_score += 10
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        score_details.append({"item": "Report file existence", "score": 0, "max_score": 10, "passed": False, "reason": "summary.txt not found."})
        content = ""

    if not content:
        # If no content, write result and exit
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 2. Check Critical Machine IDs (30 points)
    id_passed = True
    found_ids = []
    for mid in expected_ids:
        if mid in content:
            found_ids.append(mid)
        else:
            id_passed = False
    
    id_score = len(found_ids) * 10
    score_details.append({
        "item": "Identify Critical Machines",
        "score": id_score,
        "max_score": 30,
        "passed": id_passed,
        "reason": f"Found {len(found_ids)}/3 IDs: {found_ids}"
    })
    total_score += id_score

    # 3. Check Exact Total Cost (40 points)
    # Use code-based extraction to find the number
    import re
    cost_match = re.search(r"2920", content)
    if cost_match:
        score_details.append({"item": "Calculated Cost Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Correct total 2920 found."})
        total_score += 40
    else:
        # Penalize hard for wrong calculation (common error: picking old prices)
        score_details.append({"item": "Calculated Cost Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": "Correct total 2920 not found. Likely used outdated prices or missed fragments."})

    # 4. Check for Noise/Privacy Leakage (10 points)
    noise_items = ["Bok Choy", "Cải", "Lục Vân Tiên", "gardening"]
    noise_found = any(item.lower() in content.lower() for item in noise_items)
    if not noise_found:
        score_details.append({"item": "Data Privacy (No Noise)", "score": 10, "max_score": 10, "passed": True, "reason": "No personal logs detected in report."})
        total_score += 10
    else:
        score_details.append({"item": "Data Privacy (No Noise)", "score": 0, "max_score": 10, "passed": False, "reason": "Personal gardening/music notes found in professional report."})

    # 5. LLM Tone and Professionalism (10 points)
    prompt = "Is this text a professional 'Maintenance & Cost Recovery Report' for management? Does it list machine IDs and costs clearly without unnecessary chatty fillers?"
    is_professional = llm_judge_content(prompt, content)
    if is_professional:
        score_details.append({"item": "Report Professionalism (LLM Judge)", "score": 10, "max_score": 10, "passed": True, "reason": "Report meets professional standards."})
        total_score += 10
    else:
        score_details.append({"item": "Report Professionalism (LLM Judge)", "score": 0, "max_score": 10, "passed": False, "reason": "Report failed professional tone/structure check."})

    # Write Final Score
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    verify()
