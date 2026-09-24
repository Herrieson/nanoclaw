import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage (though this task is primarily structured)
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
    score = 0
    details = []
    
    target_path = os.path.join(workspace, "deliverables/summary.json")
    
    # 1. Existence check (10 points)
    if os.path.exists(target_path):
        score += 10
        details.append({"item": "Deliverable existence", "score": 10, "max_score": 10, "passed": True, "reason": "summary.json found."})
    else:
        details.append({"item": "Deliverable existence", "score": 0, "max_score": 10, "passed": False, "reason": "summary.json not found."})
        # Fatal error for calculation, but we continue to check other logic if possible
        print(json.dumps({"total_score": score, "details": details}))
        return

    # 2. Schema Validation (15 points)
    try:
        with open(target_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list) and all(isinstance(i, dict) for i in data):
            required_keys = {"name", "total_hours", "status"}
            if all(required_keys.issubset(i.keys()) for i in data):
                score += 15
                details.append({"item": "JSON Schema Validation", "score": 15, "max_score": 15, "passed": True, "reason": "Correct list of objects with required keys."})
            else:
                details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 15, "passed": False, "reason": "Missing keys in JSON objects."})
        else:
            details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 15, "passed": False, "reason": "Root is not a list of dictionaries."})
    except Exception as e:
        details.append({"item": "JSON Schema Validation", "score": 0, "max_score": 15, "passed": False, "reason": f"Parse error: {str(e)}"})
        print(json.dumps({"total_score": score, "details": details}))
        return

    # 3. Accuracy Calculation (50 points)
    # Expected values calculation:
    # U001 (Arjun Mehta): alpha(3600) + alpha(1800) + bin(3600) = 9000s = 2.5 hours. Status: active
    # U002 (Priya Sharma): alpha(-50, fail) + csv(3600) + bin(7200) = 10800s = 3.0 hours. Status: active
    # U003 (Kevin Zhang): csv(7200) = 2.0 hours. Status: active
    # U004 (Sarah Jenkins): csv(invalid, fail) = 0 hours. Status: inactive
    # U005 (Amit Patel): bin(-999, fail) = 0 hours. Status: inactive
    
    expected = {
        "Arjun Mehta": {"hours": 2.5, "status": "active"},
        "Priya Sharma": {"hours": 3.0, "status": "active"},
        "Kevin Zhang": {"hours": 2.0, "status": "active"},
        "Sarah Jenkins": {"hours": 0.0, "status": "inactive"},
        "Amit Patel": {"hours": 0.0, "status": "inactive"}
    }
    
    found_users = {item['name']: item for item in data}
    calc_score = 0
    for name, exp in expected.items():
        if name in found_users:
            user_data = found_users[name]
            # Check hours (float tolerance) and status
            if abs(user_data['total_hours'] - exp['hours']) < 0.01 and user_data['status'] == exp['status']:
                calc_score += 10
            elif abs(user_data['total_hours'] - exp['hours']) < 0.01:
                calc_score += 5 # Right hours, wrong status
    
    score += calc_score
    details.append({"item": "Data Accuracy (5 users check)", "score": calc_score, "max_score": 50, "passed": calc_score == 50, "reason": f"User calculations correct: {calc_score}/50"})

    # 4. Identity Resolution Verification (25 points)
    # Specifically check if "Arjun Mehta" was resolved correctly (he was not in the CSV)
    arjun_data = found_users.get("Arjun Mehta")
    if arjun_data and abs(arjun_data['total_hours'] - 2.5) < 0.01:
        score += 25
        details.append({"item": "Identity Resolution (U001)", "score": 25, "max_score": 25, "passed": True, "reason": "Successfully resolved Arjun Mehta from API and aggregated his logs."})
    else:
        details.append({"item": "Identity Resolution (U001)", "score": 0, "max_score": 25, "passed": False, "reason": "Arjun Mehta missing or data incorrect (requires API usage)."})

    # Final Score write-back
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(score), "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
