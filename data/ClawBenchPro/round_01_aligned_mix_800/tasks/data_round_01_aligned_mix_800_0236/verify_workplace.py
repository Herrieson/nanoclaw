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
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def extract_numbers_from_json(obj):
    """Recursively extract all numeric values from a JSON object."""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.update(extract_numbers_from_json(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(extract_numbers_from_json(item))
    elif isinstance(obj, (int, float)):
        found.add(obj)
    elif isinstance(obj, str):
        try:
            found.add(float(obj))
        except ValueError:
            pass
    return found

def extract_strings_from_json(obj):
    """Recursively extract all string values and keys from a JSON object."""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.add(k.lower())
            found.update(extract_strings_from_json(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(extract_strings_from_json(item))
    elif isinstance(obj, str):
        found.add(obj.lower())
    return found

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverables_path, "fundraiser_summary.json")

    results = []
    total_score = 0
    
    # 1. Check Directory and File Existence (10 Points)
    file_exists = os.path.isfile(summary_file)
    if file_exists:
        results.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"{summary_file} exists."})
        total_score += 10
    else:
        results.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"{summary_file} is missing."})
        
    data = None
    if file_exists:
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append({"item": "检查JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format."})
            total_score += 10
        except json.JSONDecodeError:
            results.append({"item": "检查JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON format."})

    if data:
        nums = extract_numbers_from_json(data)
        strs = extract_strings_from_json(data)
        
        # 2. Check Approved Hours Calculation (20 Points)
        if 14 in nums or 14.0 in nums:
            results.append({"item": "计算授权志愿者总时长", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly calculated 14 hours."})
            total_score += 20
        else:
            results.append({"item": "计算授权志愿者总时长", "score": 0, "max_score": 20, "passed": False, "reason": "Did not find the exact value 14 in parsed numeric data."})
            
        # 3. Check Projected Revenue Calculation (20 Points)
        if 78 in nums or 78.0 in nums:
            results.append({"item": "计算授权唱片总估值", "score": 20, "max_score": 20, "passed": True, "reason": "Correctly calculated $78 revenue."})
            total_score += 20
        else:
            results.append({"item": "计算授权唱片总估值", "score": 0, "max_score": 20, "passed": False, "reason": "Did not find the exact value 78 in parsed numeric data."})
            
        # 4. Check Data Purity and Distraction Filtering (20 Points)
        has_pollution = False
        pollution_reasons = []
        forbidden_names = ["dave", "eve", "evans", "white"]
        forbidden_nums = [10, 10.0, 1, 1.0, 40, 40.0, 25, 25.0, 118, 118.0]
        forbidden_subjects = ["math", "history", "science", "grade", "midterm"]
        
        for name in forbidden_names:
            if any(name in s for s in strs):
                has_pollution = True
                pollution_reasons.append(f"Found unapproved name: {name}")
                
        for subject in forbidden_subjects:
            if any(subject in s for s in strs):
                has_pollution = True
                pollution_reasons.append(f"Found student grades decoy data: {subject}")
                
        for num in forbidden_nums:
            if num in nums:
                has_pollution = True
                pollution_reasons.append(f"Found unapproved or mixed aggregated value: {num}")
                
        if not has_pollution:
            results.append({"item": "数据纯净度检查", "score": 20, "max_score": 20, "passed": True, "reason": "Successfully filtered out unapproved personnel and decoy files."})
            total_score += 20
        else:
            results.append({"item": "数据纯净度检查", "score": 0, "max_score": 20, "passed": False, "reason": f"Data polluted: {', '.join(pollution_reasons)}"})

        # 5. LLM Semantic Verification for Formal Summary (20 Points)
        prompt = (
            "Does the following JSON text (representing a summary report for a community center board) "
            "maintain a formal tone AND explicitly indicate that the data is only for 'approved', 'authorized', or 'whitelisted' volunteers/donations?"
        )
        is_formal_and_explicit = llm_judge_content(prompt, json.dumps(data))
        if is_formal_and_explicit:
            results.append({"item": "LLM语义检查（摘要正式性与范围明确性）", "score": 20, "max_score": 20, "passed": True, "reason": "LLM confirmed the summary is formal and explicitly mentions approved volunteers."})
            total_score += 20
        else:
            results.append({"item": "LLM语义检查（摘要正式性与范围明确性）", "score": 0, "max_score": 20, "passed": False, "reason": "LLM rejected the formality or explicit scope declaration of the summary."})
    else:
        # Cascade fail
        results.extend([
            {"item": "计算授权志愿者总时长", "score": 0, "max_score": 20, "passed": False, "reason": "Missing valid JSON file."},
            {"item": "计算授权唱片总估值", "score": 0, "max_score": 20, "passed": False, "reason": "Missing valid JSON file."},
            {"item": "数据纯净度检查", "score": 0, "max_score": 20, "passed": False, "reason": "Missing valid JSON file."},
            {"item": "LLM语义检查（摘要正式性与范围明确性）", "score": 0, "max_score": 20, "passed": False, "reason": "Missing valid JSON file."}
        ])

    output = {
        "total_score": total_score,
        "details": results
    }

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
