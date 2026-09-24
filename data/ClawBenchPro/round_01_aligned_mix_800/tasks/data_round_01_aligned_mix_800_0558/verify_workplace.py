import os
import sys
import json
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
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Check]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "official_safety_report.json")
    
    score_details = []
    total_score = 0
    
    # 1. Check if the output file exists
    if os.path.exists(report_path):
        score_details.append({"item": "Deliverable file exists", "score": 10, "max_score": 10, "passed": True, "reason": "official_safety_report.json found."})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable file exists", "score": 0, "max_score": 10, "passed": False, "reason": "official_safety_report.json is missing."})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check JSON schema
    report_data = None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        if isinstance(report_data, dict) and "total_man_hours" in report_data and "safety_violations" in report_data:
            score_details.append({"item": "JSON Schema Validation", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON with required keys."})
            total_score += 10
        else:
            score_details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 10, "passed": False, "reason": "JSON structure is incorrect. Missing required keys."})
    except Exception as e:
        score_details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 10, "passed": False, "reason": f"File is not a valid JSON: {e}"})
    
    if not report_data or not isinstance(report_data, dict):
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Check exact total_man_hours calculation
    hours = report_data.get("total_man_hours", 0)
    try:
        hours = float(hours)
        if hours == 80:
            score_details.append({"item": "Total Man Hours Accuracy", "score": 30, "max_score": 30, "passed": True, "reason": "Correctly calculated total man-hours as 80."})
            total_score += 30
        else:
            score_details.append({"item": "Total Man Hours Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": f"Incorrect man-hours calculation. Expected 80, got {hours}."})
    except (ValueError, TypeError):
        score_details.append({"item": "Total Man Hours Accuracy", "score": 0, "max_score": 30, "passed": False, "reason": "total_man_hours is not a valid number."})

    # 4. Filter and count violations
    violations = report_data.get("safety_violations", [])
    if not isinstance(violations, list):
        score_details.append({"item": "Violations Data Type", "score": 0, "max_score": 10, "passed": False, "reason": "safety_violations must be a list."})
    else:
        if len(violations) == 4:
            score_details.append({"item": "Violations Count", "score": 10, "max_score": 10, "passed": True, "reason": "Extracted exactly 4 genuine workplace violations."})
            total_score += 10
        else:
            score_details.append({"item": "Violations Count", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected exactly 4 violations, but found {len(violations)}. You may have missed some or failed to filter out personal memos."})

        # 5. Semantic validation of violations
        # We need to verify that 4 hazards are mentioned: scaffolding, exposed wiring, hard hats, unsecured trench.
        # And it MUST NOT contain personal life issues: toddler, easel, paint, canvas, art, kids, kitchen.
        violations_text = "\n".join([str(v) for v in violations])
        
        # Check negative constraint first (Hallucination/Personal items check)
        prompt_negative = (
            "Does the following text contain any mention of personal or non-workplace items, "
            "specifically things like: art, paint, canvas, easel, kids, toddler, or kitchen? "
            "If it contains ANY of these, answer YES. If it is purely about construction site hazards, answer NO."
        )
        has_personal_items = llm_judge_content(prompt_negative, violations_text)
        
        if not has_personal_items:
            score_details.append({"item": "LLM Semantic Check: No Personal Items", "score": 20, "max_score": 20, "passed": True, "reason": "Successfully filtered out personal and art-related items."})
            total_score += 20
        else:
            score_details.append({"item": "LLM Semantic Check: No Personal Items", "score": 0, "max_score": 20, "passed": False, "reason": "Failed to filter out personal/art hazards (e.g., kids, paint, easel)."})

        # Check positive constraints (Are the 4 actual hazards captured?)
        prompt_positive = (
            "Does the following text accurately cover ALL FOUR of these specific construction site safety hazards: "
            "1) A scaffolding missing a guardrail. "
            "2) Exposed wiring near a water line. "
            "3) Subcontractors not wearing hard hats. "
            "4) An unsecured trench over 5 feet deep left by a backhoe operator. "
            "Answer YES if all 4 issues are clearly present. Otherwise answer NO."
        )
        has_all_hazards = llm_judge_content(prompt_positive, violations_text)
        
        if has_all_hazards:
            score_details.append({"item": "LLM Semantic Check: Genuine Hazards Coverage", "score": 20, "max_score": 20, "passed": True, "reason": "All 4 genuine hazards were correctly captured."})
            total_score += 20
        else:
            score_details.append({"item": "LLM Semantic Check: Genuine Hazards Coverage", "score": 0, "max_score": 20, "passed": False, "reason": "Did not capture all 4 required workplace hazards accurately."})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
