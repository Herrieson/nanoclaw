import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client with SSL verification disabled
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    Optional LLM evaluation method for unstructured content.
    Currently used as fallback if unstructured responses are detected.
    """
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
    
    # 1. Directory exists (10 points)
    dir_path = os.path.join(workspace, "manager_desk")
    if os.path.isdir(dir_path):
        score_details.append({"item": "Check if directory 'manager_desk' exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists"})
        total_score += 10
    else:
        score_details.append({"item": "Check if directory 'manager_desk' exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'manager_desk' not found"})
        
    # 2. File exists (10 points)
    file_path = os.path.join(dir_path, "tip_summary.json")
    if os.path.isdir(dir_path) and os.path.isfile(file_path):
        score_details.append({"item": "Check if file 'tip_summary.json' exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
        total_score += 10
    else:
        score_details.append({"item": "Check if file 'tip_summary.json' exists", "score": 0, "max_score": 10, "passed": False, "reason": "File 'tip_summary.json' not found"})
        
    # 3. JSON formatting and exact keys (20 points)
    json_data = None
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            expected_keys = {"total_valid_tips", "boh_hourly_rate", "foh_hourly_rate"}
            actual_keys = set(json_data.keys())
            
            if expected_keys.issubset(actual_keys):
                if len(actual_keys) == len(expected_keys):
                    score_details.append({"item": "Validate JSON format and exact schema", "score": 20, "max_score": 20, "passed": True, "reason": "Contains exactly the 3 required keys with no hallucinations."})
                    total_score += 20
                else:
                    score_details.append({"item": "Validate JSON format and exact schema", "score": 10, "max_score": 20, "passed": False, "reason": f"Contains required keys, but includes extra hallucinated keys: {actual_keys - expected_keys}. Penalty applied."})
                    total_score += 10
            else:
                score_details.append({"item": "Validate JSON format and exact schema", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing required keys. Missing: {expected_keys - actual_keys}"})
        except Exception as e:
            score_details.append({"item": "Validate JSON format and exact schema", "score": 0, "max_score": 20, "passed": False, "reason": f"Failed to parse JSON cleanly: {e}"})
    else:
        score_details.append({"item": "Validate JSON format and exact schema", "score": 0, "max_score": 20, "passed": False, "reason": "File does not exist, skipped JSON check."})
        
    # Helper for rigorous numeric checking
    def check_value(key, expected, tol, max_score, allow_rounding_to_2_decimals=False):
        if json_data and key in json_data:
            try:
                val = float(json_data[key])
                if abs(val - expected) < tol:
                    return {"item": f"Check numerical precision for {key}", "score": max_score, "max_score": max_score, "passed": True, "reason": f"{key} calculated perfectly: {val}"}
                elif allow_rounding_to_2_decimals and abs(val - round(expected, 2)) < tol:
                    return {"item": f"Check numerical precision for {key}", "score": max_score, "max_score": max_score, "passed": True, "reason": f"{key} calculated correctly with 2 decimal rounding: {val}"}
                else:
                    return {"item": f"Check numerical precision for {key}", "score": 0, "max_score": max_score, "passed": False, "reason": f"{key} value incorrect. Expected ~{expected}, Got {val}"}
            except (ValueError, TypeError):
                return {"item": f"Check numerical precision for {key}", "score": 0, "max_score": max_score, "passed": False, "reason": f"Value for {key} could not be parsed as float. No string texts are allowed here."}
        else:
            return {"item": f"Check numerical precision for {key}", "score": 0, "max_score": max_score, "passed": False, "reason": f"Missing key {key}"}

    # 4. total_valid_tips = 38.0 (20 points)
    res_total = check_value("total_valid_tips", 38.0, 1e-3, 20)
    score_details.append(res_total)
    total_score += res_total["score"]
    
    # 5. boh_hourly_rate = 0.152 (20 points)
    res_boh = check_value("boh_hourly_rate", 0.152, 1e-4, 20, allow_rounding_to_2_decimals=True)
    score_details.append(res_boh)
    total_score += res_boh["score"]
    
    # 6. foh_hourly_rate = 0.19 (20 points)
    res_foh = check_value("foh_hourly_rate", 0.190, 1e-4, 20, allow_rounding_to_2_decimals=True)
    score_details.append(res_foh)
    total_score += res_foh["score"]
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
