import os
import sys
import json
import httpx
from openai import OpenAI

# --- Configuration ---
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

def calculate_score(workspace):
    score = 0
    details = []
    report_path = os.path.join(workspace, "community_fair_prep")
    
    # 1. Basic Structure (10 pts)
    if os.path.exists(report_path) and os.path.isdir(report_path):
        score += 10
        details.append({"item": "Directory Structure", "score": 10, "max_score": 10, "passed": True, "reason": "Folder 'community_fair_prep' found."})
    else:
        details.append({"item": "Directory Structure", "score": 0, "max_score": 10, "passed": False, "reason": "Folder 'community_fair_prep' not found."})
        return score, details # Fatal flaw

    # Find the report file (allow common naming like report.txt or report.md)
    report_files = [f for f in os.listdir(report_path) if f.endswith(('.txt', '.md', '.json'))]
    if not report_files:
        details.append({"item": "Report File Presence", "score": 0, "max_score": 10, "passed": False, "reason": "No report file found in folder."})
        return score, details
    
    report_file = os.path.join(report_path, report_files[0])
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Volunteer Validation (30 pts)
    # Correct Validated Hours: Sarah(4.5) + David(2.0) + Miriam(1.5) + Jamal(4.0) + Ezra(3.0) = 15.0
    # Correct Frauds: Chad, Karen
    has_sarah = "Sarah" in content
    has_jamal = "Jamal" in content
    has_total_15 = "15" in content or "15.0" in content
    has_frauds = "Chad" in content and "Karen" in content
    
    v_score = 0
    if has_sarah and has_jamal: v_score += 10
    if has_total_15: v_score += 10
    if has_frauds: v_score += 10
    
    score += v_score
    details.append({"item": "Volunteer Validation Logic", "score": v_score, "max_score": 30, "passed": v_score == 30, 
                    "reason": f"Found valid names: {has_sarah}, Correct Total: {has_total_15}, Found Frauds: {has_frauds}"})

    # 3. Donation Filtering (40 pts)
    # Healthy (>60): Organic Apples (95), Meditation Cushions (100), Social Justice Pamphlets (100), Whole Wheat Bread (85)
    # Trash (<=60): Candy Bars (12), Soda Cans (5), Processed Cheese (40)
    
    approved_items = ["Organic Apples", "Meditation Cushions", "Social Justice Pamphlets", "Whole Wheat Bread"]
    rejected_items = ["Candy Bars", "Soda Cans", "Processed Cheese"]
    
    all_approved_found = all(item.lower() in content.lower() for item in approved_items)
    any_rejected_found = any(item.lower() in content.lower() for item in rejected_items)
    
    d_score = 0
    if all_approved_found: d_score += 25
    if not any_rejected_found: d_score += 15
    else: d_score -= 10 # Penalty for including junk food
    
    score += max(0, d_score)
    details.append({"item": "Nutritional Filtering", "score": max(0, d_score), "max_score": 40, "passed": d_score == 40, 
                    "reason": f"All healthy items present: {all_approved_found}. Any junk food included: {any_rejected_found}"})

    # 4. LLM Semantic Check (20 pts)
    # Check for professional tone and table structure
    prompt = "Check if the report contains a table for donations and maintains a professional, organized tone suitable for a community leader."
    is_professional = llm_judge_content(prompt, content)
    if is_professional:
        score += 20
        details.append({"item": "Professionalism & Formatting", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified professional tone and table structure."})
    else:
        details.append({"item": "Professionalism & Formatting", "score": 0, "max_score": 20, "passed": False, "reason": "LLM found formatting or tone lacking."})

    return score, details

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    total, d_list = calculate_score(workspace_dir)
    output = {"total_score": total, "details": d_list}
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
