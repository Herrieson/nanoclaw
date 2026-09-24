import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# Constants & API Configuration
# ----------------------------------------------------------------
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
    """Utility for semantic validation using LLM."""
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

# ----------------------------------------------------------------
# Main Logic
# ----------------------------------------------------------------

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "deliverables/audit_final_report.json")
    
    score_details = []
    total_score = 0

    # 1. Check if the file exists (10 points)
    if os.path.exists(deliverable_path):
        score_details.append({"item": "Deliverable Existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found audit_final_report.json"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable Existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing audit_final_report.json"})
        # Write results early if file missing
        save_results(total_score, score_details)
        return

    # 2. Parse JSON and Check Structure (10 points)
    try:
        with open(deliverable_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ["unauthorized_badge_ids", "total_hours_sum"]
        if all(k in data for k in required_keys):
            score_details.append({"item": "JSON Structure Integrity", "score": 10, "max_score": 10, "passed": True, "reason": "Correct keys found"})
            total_score += 10
        else:
            score_details.append({"item": "JSON Structure Integrity", "score": 0, "max_score": 10, "passed": False, "reason": "Missing required keys"})
    except Exception as e:
        score_details.append({"item": "JSON Syntax", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        save_results(total_score, score_details)
        return

    # 3. Verify Unauthorized Badge IDs (40 points)
    # Correct IDs based on env_builder: ["X-999", "Z-404", "MAL-007"]
    # Logic: After 22:00 or before 05:00. 
    expected_ids = {"X-999", "Z-404", "MAL-007"}
    actual_ids = set(data.get("unauthorized_badge_ids", []))
    
    if actual_ids == expected_ids:
        score_details.append({"item": "Unauthorized Access IDs", "score": 40, "max_score": 40, "passed": True, "reason": "Identified all 3 correct unauthorized IDs"})
        total_score += 40
    elif actual_ids.intersection(expected_ids):
        partial = len(actual_ids.intersection(expected_ids)) * 10
        score_details.append({"item": "Unauthorized Access IDs", "score": partial, "max_score": 40, "passed": False, "reason": f"Partially correct. Identified: {actual_ids}"})
        total_score += partial
    else:
        score_details.append({"item": "Unauthorized Access IDs", "score": 0, "max_score": 40, "passed": False, "reason": "No correct unauthorized IDs identified"})

    # 4. Verify Total Hours Sum (40 points)
    # Ground Truth Calculation:
    # N-201: 3 shifts * 12.0h = 36.0h
    # N-202: 2 distinct shifts (one was duplicated) * 8.0h = 16.0h
    # Total = 36.0 + 16.0 = 52.0
    # Note: Decoy file has 9999.99
    try:
        total_hours = float(data.get("total_hours_sum", 0))
        if abs(total_hours - 52.0) < 0.01:
            score_details.append({"item": "Total Hours Calculation (Deduplicated)", "score": 40, "max_score": 40, "passed": True, "reason": "Correct total of 52.0 hours calculated after de-duplication"})
            total_score += 40
        elif abs(total_hours - 60.0) < 0.01:
            # Failed to de-duplicate the N-202 entry (8.0h duplicate)
            score_details.append({"item": "Total Hours Calculation (Deduplicated)", "score": 15, "max_score": 40, "passed": False, "reason": "Failed to de-duplicate logs (got 60.0 instead of 52.0)"})
            total_score += 15
        elif abs(total_hours - 9999.99) < 0.01:
            score_details.append({"item": "Total Hours Calculation (Deduplicated)", "score": 0, "max_score": 40, "passed": False, "reason": "Agent fell for the decoy DRAFT summary file"})
        else:
            score_details.append({"item": "Total Hours Calculation (Deduplicated)", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect total: {total_hours}"})
    except:
        score_details.append({"item": "Total Hours Value Type", "score": 0, "max_score": 40, "passed": False, "reason": "Could not parse hours as a number"})

    save_results(total_score, score_details)

def save_results(score, details):
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2)

if __name__ == "__main__":
    run_verification()
