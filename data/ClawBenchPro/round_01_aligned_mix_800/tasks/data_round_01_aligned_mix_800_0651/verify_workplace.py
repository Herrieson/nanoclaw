import os
import sys
import json
import re
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
    results_dir = os.path.join(workspace, "results")
    callback_file = os.path.join(results_dir, "callback_list.json")
    supplies_file = os.path.join(results_dir, "supplies_needed.txt")

    total_score = 0
    details = []

    # 1. 检查 results 目录是否存在
    if os.path.isdir(results_dir):
        total_score += 10
        details.append({"item": "Results Directory", "score": 10, "max_score": 10, "passed": True, "reason": "'results' directory exists."})
    else:
        details.append({"item": "Results Directory", "score": 0, "max_score": 10, "passed": False, "reason": "'results' directory is missing."})
        # If no results dir, can't continue checking files effectively
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查 callback_list.json 文件是否存在
    if os.path.isfile(callback_file):
        total_score += 10
        details.append({"item": "Callback List File Existence", "score": 10, "max_score": 10, "passed": True, "reason": "callback_list.json found."})
        
        # 3. 检查 JSON 格式合法性
        try:
            with open(callback_file, "r") as f:
                callback_data = json.load(f)
            
            if isinstance(callback_data, list):
                total_score += 15
                details.append({"item": "Callback List Format", "score": 15, "max_score": 15, "passed": True, "reason": "Valid JSON list structure."})
                
                # 4. 检查 Callback List 核心数据 (必须且仅包含 102, 103, 104, 108)
                expected_ids = {"102", "103", "104", "108"}
                actual_ids = {str(pid) for pid in callback_data}
                
                if actual_ids == expected_ids:
                    total_score += 35
                    details.append({"item": "Callback Data Accuracy", "score": 35, "max_score": 35, "passed": True, "reason": "Exactly identified all correct callback patients."})
                else:
                    missing = expected_ids - actual_ids
                    extra = actual_ids - expected_ids
                    reason = "Mismatch in patients."
                    if missing: reason += f" Missing: {missing}."
                    if extra: reason += f" Extra/Hallucinated: {extra}."
                    details.append({"item": "Callback Data Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": reason})
                    
            else:
                details.append({"item": "Callback List Format", "score": 0, "max_score": 15, "passed": False, "reason": "JSON root is not a list."})
                details.append({"item": "Callback Data Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "Cannot verify data due to wrong format."})
                
        except json.JSONDecodeError:
            details.append({"item": "Callback List Format", "score": 0, "max_score": 15, "passed": False, "reason": "Invalid JSON file (parse error)."})
            details.append({"item": "Callback Data Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "Cannot verify data due to invalid JSON."})
    else:
        details.append({"item": "Callback List File Existence", "score": 0, "max_score": 10, "passed": False, "reason": "callback_list.json missing."})
        details.append({"item": "Callback List Format", "score": 0, "max_score": 15, "passed": False, "reason": "Missing file."})
        details.append({"item": "Callback Data Accuracy", "score": 0, "max_score": 35, "passed": False, "reason": "Missing file."})

    # 5. 检查 supplies_needed.txt 及计算逻辑
    if os.path.isfile(supplies_file):
        with open(supplies_file, "r") as f:
            supplies_content = f.read().strip()
            
        # Extract numbers using regex
        numbers = re.findall(r'\d+', supplies_content)
        if numbers:
            # The total kits used could be 12 (if booth 1 kept for dupes) or 11 (if booth 2 kept for dupes). Both are valid deduplication outcomes.
            value = int(numbers[0])
            if value in [11, 12]:
                total_score += 30
                details.append({"item": "Supplies Calculation", "score": 30, "max_score": 30, "passed": True, "reason": f"Correct total kits calculated: {value}."})
            else:
                details.append({"item": "Supplies Calculation", "score": 0, "max_score": 30, "passed": False, "reason": f"Incorrect total kits calculated. Found: {value}. Expected 11 or 12."})
        else:
            details.append({"item": "Supplies Calculation", "score": 0, "max_score": 30, "passed": False, "reason": "No numeric value found in supplies_needed.txt."})
    else:
        details.append({"item": "Supplies Calculation", "score": 0, "max_score": 30, "passed": False, "reason": "supplies_needed.txt missing."})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
