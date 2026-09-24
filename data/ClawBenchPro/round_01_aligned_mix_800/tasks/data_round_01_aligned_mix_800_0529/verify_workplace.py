import os
import sys
import json
import httpx
from openai import OpenAI

def get_env_var(key, default):
    return os.environ.get(key, default)

MOCK_API_KEY = get_env_var("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = get_env_var("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = get_env_var("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize OpenAI client
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
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "accounting", "final_report.json")
    
    # 1. Check Directory and File Existence (10 pts)
    if os.path.exists(report_path):
        score_details.append({"item": "Final report existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found report at accounting/final_report.json"})
        total_score += 10
    else:
        score_details.append({"item": "Final report existence", "score": 0, "max_score": 10, "passed": False, "reason": "Report not found"})
        # Write scores early if file missing
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. Check JSON validity (10 pts)
    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
        score_details.append({"item": "JSON format validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON format validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. Precision Check - Labor Cost (30 pts)
    # Expected: 4500.5 (Apex) + 3100 (Fox) + 3000 (Baja) + 4000 (Maverick) = 14600.5
    expected_labor = 14600.5
    actual_labor = data.get("total_labor_costs", 0)
    if abs(float(actual_labor) - expected_labor) < 0.01:
        score_details.append({"item": "Total Labor Cost Calculation", "score": 30, "max_score": 30, "passed": True, "reason": "Labor cost matches exactly (14600.5)"})
        total_score += 30
    else:
        score_details.append({"item": "Total Labor Cost Calculation", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {expected_labor}, got {actual_labor}"})

    # 4. Precision Check - Material Cost (30 pts)
    # Expected: 8200 (Apex) + 6200 (Fox) + 1500 (Baja) + 1000 (Maverick) = 16900.0
    expected_mat = 16900.0
    actual_mat = data.get("total_material_costs", 0)
    if abs(float(actual_mat) - expected_mat) < 0.01:
        score_details.append({"item": "Total Material Cost Calculation", "score": 30, "max_score": 30, "passed": True, "reason": "Material cost matches exactly (16900.0)"})
        total_score += 30
    else:
        score_details.append({"item": "Total Material Cost Calculation", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {expected_mat}, got {actual_mat}"})

    # 5. Contractor List & Filtering Verification (20 pts)
    # Must include the 4 valid ones, must NOT include pending/false/ghost
    expected_names = {"Apex Framing", "Desert Fox Concrete", "Baja Dirt Works", "Maverick Excavation"}
    actual_names = set(data.get("approved_contractors", []))
    
    invalid_names = {"Rogue Welding", "Sloppy Joe Painters", "Ghost Services"}
    found_invalid = actual_names.intersection(invalid_names)
    missing_valid = expected_names - actual_names
    
    if not found_invalid and not missing_valid:
        score_details.append({"item": "Contractor Filtering (W-9 compliance)", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly identified all and only approved contractors"})
        total_score += 20
    elif found_invalid:
        score_details.append({"item": "Contractor Filtering (W-9 compliance)", "score": 0, "max_score": 20, "passed": False, "reason": f"Included unapproved contractors: {found_invalid}"})
    else:
        score_details.append({"item": "Contractor Filtering (W-9 compliance)", "score": 10, "max_score": 20, "passed": False, "reason": f"Missed approved contractors: {missing_valid}"})

    # Final result writing
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    verify()
