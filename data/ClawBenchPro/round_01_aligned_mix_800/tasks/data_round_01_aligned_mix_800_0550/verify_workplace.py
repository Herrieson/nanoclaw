import os
import sys
import json
import httpx
from openai import OpenAI

# Configuration for potential LLM usage
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
    score_details = []
    total_score = 0

    # 1. Check Directory and File Existence (10 points)
    target_dir = os.path.join(workspace, "desk_drawer")
    target_file = os.path.join(target_dir, "report.json")
    
    dir_exists = os.path.exists(target_dir)
    file_exists = os.path.exists(target_file)
    
    if dir_exists and file_exists:
        score_details.append({"item": "Directory and report file existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found desk_drawer/report.json"})
        total_score += 10
    else:
        score_details.append({"item": "Directory and report file existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing desk_drawer/report.json"})
        # Write preliminary failure
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. Content Structure and JSON Schema (10 points)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        
        has_keys = "compromised_plots" in data and "total_safe_yield" in data
        is_list = isinstance(data.get("compromised_plots"), list)
        is_int = isinstance(data.get("total_safe_yield"), int)
        
        if has_keys and is_list and is_int:
            score_details.append({"item": "JSON structure and data types", "score": 10, "max_score": 10, "passed": True, "reason": "JSON keys and types are correct"})
            total_score += 10
        else:
            score_details.append({"item": "JSON structure and data types", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid keys or types: {type(data.get('compromised_plots'))}, {type(data.get('total_safe_yield'))}"})
    except Exception as e:
        score_details.append({"item": "JSON parsing", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. Validation of Compromised Plots (40 points)
    # Ground Truth: ["ORG-013", "ORG-042", "ORG-088", "ORG-105", "ORG-149"]
    expected_compromised = sorted(["ORG-013", "ORG-042", "ORG-088", "ORG-105", "ORG-149"])
    actual_compromised = sorted(data.get("compromised_plots", []))
    
    if actual_compromised == expected_compromised:
        score_details.append({"item": "Compromised plots identification (Exact match)", "score": 40, "max_score": 40, "passed": True, "reason": "Correctly identified all compromised organic plots."})
        total_score += 40
    elif set(actual_compromised).issubset(set(expected_compromised)) and len(actual_compromised) > 0:
        score_details.append({"item": "Compromised plots identification (Partial match)", "score": 15, "max_score": 40, "passed": False, "reason": f"Partial match. Expected {expected_compromised}, got {actual_compromised}"})
        total_score += 15
    else:
        score_details.append({"item": "Compromised plots identification", "score": 0, "max_score": 40, "passed": False, "reason": f"Incorrect plots or included conventional farms. Got: {actual_compromised}"})

    # 4. Validation of Total Safe Yield (40 points)
    # Ground Truth: 155928
    # Calculation Logic Check: Total (161325) - Compromised (5397) = 155928
    expected_yield = 155928
    actual_yield = data.get("total_safe_yield")
    
    if actual_yield == expected_yield:
        score_details.append({"item": "Total safe yield calculation (Exact)", "score": 40, "max_score": 40, "passed": True, "reason": "Yield calculation is perfectly accurate."})
        total_score += 40
    elif abs(actual_yield - expected_yield) <= 2000: # Allowing minor error if they missed one plot or had slight parsing bug but showed process
        score_details.append({"item": "Total safe yield calculation (Close approximation)", "score": 10, "max_score": 40, "passed": False, "reason": f"Yield is close but incorrect. Expected {expected_yield}, got {actual_yield}"})
        total_score += 10
    else:
        score_details.append({"item": "Total safe yield calculation", "score": 0, "max_score": 40, "passed": False, "reason": f"Yield is significantly incorrect. Got {actual_yield}"})

    # Final Summary
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
