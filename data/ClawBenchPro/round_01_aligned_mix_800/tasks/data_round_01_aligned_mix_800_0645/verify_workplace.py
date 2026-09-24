import os
import sys
import json
import httpx
from openai import OpenAI

# -------------------------------------------------------------------
# Configuration & LLM Setup
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Validation Logic
# -------------------------------------------------------------------
def verify_workplace(workspace):
    total_score = 0
    details = []
    
    target_dir = os.path.join(workspace, "agency_audit")
    target_file = os.path.join(target_dir, "final_report.json")
    
    # Check 1: Directory & File Existence (10 pts)
    item_exist = {"item": "检查目标目录和文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if os.path.isdir(target_dir) and os.path.isfile(target_file):
        item_exist["score"] = 10
        item_exist["passed"] = True
        item_exist["reason"] = "`agency_audit/final_report.json` exists."
    else:
        item_exist["reason"] = "`agency_audit/final_report.json` missing."
    details.append(item_exist)
    total_score += item_exist["score"]

    # If file doesn't exist, we can't do further checks
    if not item_exist["passed"]:
        return {"total_score": total_score, "details": details}

    # Read File Content
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        details.append({"item": "读取文件", "score": 0, "max_score": 0, "passed": False, "reason": f"Read error: {e}"})
        return {"total_score": total_score, "details": details}

    # Check 2: Strict JSON Schema Validity (10 pts)
    item_json = {"item": "检查结果是否为合法且结构化的 JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        json_data = json.loads(raw_content)
        item_json["score"] = 10
        item_json["passed"] = True
        item_json["reason"] = "Valid JSON format."
    except json.JSONDecodeError:
        item_json["reason"] = "Failed to parse JSON. Content is not valid structured data."
        details.append(item_json)
        return {"total_score": total_score, "details": details} # Fatal error for data checks
    details.append(item_json)
    total_score += item_json["score"]

    # Helper function to recursively find numeric and list data
    def extract_values(obj):
        nums = []
        lists = []
        if isinstance(obj, dict):
            for v in obj.values():
                n, l = extract_values(v)
                nums.extend(n)
                lists.extend(l)
        elif isinstance(obj, list):
            lists.append(obj)
            for v in obj:
                n, l = extract_values(v)
                nums.extend(n)
                lists.extend(l)
        elif isinstance(obj, (int, float)):
            nums.append(obj)
        return nums, lists

    nums, lists = extract_values(json_data)

    # Check 3: Deterministic check for total spend (40 pts)
    # Expected spend: (@creative_max: 5*150=750) + (@art_guru: 3*200=600) + (@trend_setter: 2*350=700) + (@digital_nomad: 8*120=960) + (@pixel_perfect: 1*500=500) = 3510
    expected_total = 3510
    item_total = {"item": "精准验证计算出的合法授权人总费用", "score": 0, "max_score": 40, "passed": False, "reason": ""}
    if expected_total in nums:
        item_total["score"] = 40
        item_total["passed"] = True
        item_total["reason"] = f"Correctly calculated total spend: {expected_total}."
    else:
        item_total["reason"] = f"Total spend {expected_total} not found in numeric values. Found numbers: {nums}"
    details.append(item_total)
    total_score += item_total["score"]

    # Check 4: Deterministic check for unauthorized influencers (30 pts)
    # Expected intruders: @hacker_scammer, @fake_bot_99, @mystery_guest
    expected_intruders = {"@hacker_scammer", "@fake_bot_99", "@mystery_guest"}
    item_intruders = {"item": "精准验证未授权入侵者名单", "score": 0, "max_score": 30, "passed": False, "reason": ""}
    
    found_correct_list = False
    for lst in lists:
        str_list = {str(x) for x in lst if isinstance(x, str)}
        if expected_intruders.issubset(str_list):
            if len(str_list) == len(expected_intruders):
                found_correct_list = True
                item_intruders["reason"] = "Successfully extracted exact unauthorized list."
                break
            else:
                item_intruders["reason"] = "Extracted list contains intruders but also includes hallucinated/incorrect accounts."
                item_intruders["score"] = 15 # Partial points for having them, but with noise
                break
    
    if found_correct_list:
        item_intruders["score"] = 30
        item_intruders["passed"] = True
    elif item_intruders["score"] == 0:
        item_intruders["reason"] = "Did not find a list containing all unauthorized accounts."

    details.append(item_intruders)
    total_score += item_intruders["score"]

    # Check 5: Semantic verification of JSON structure and keys (10 pts)
    item_semantic = {"item": "利用大模型检查 JSON 键名与结构的专业性和易读性", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    prompt_text = (
        "Check if the following JSON content serves as a 'clean summary' of an agency audit. "
        "It MUST have clear, descriptive keys for the 'unauthorized accounts/intruders' and the 'total spend'. "
        "Return YES if the keys are appropriately named (e.g., 'intruders', 'unauthorized', 'total_spend', 'total_bill'). "
        "Return NO if it consists of raw numbers without descriptive labels or is extremely vague."
    )
    is_professional = llm_judge_content(prompt_text, raw_content)
    if is_professional:
        item_semantic["score"] = 10
        item_semantic["passed"] = True
        item_semantic["reason"] = "JSON keys are semantically appropriate."
    else:
        item_semantic["reason"] = "JSON keys lack clear semantic meaning or are missing."
    details.append(item_semantic)
    total_score += item_semantic["score"]

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(workspace)
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
